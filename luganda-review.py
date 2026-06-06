#!/usr/bin/env python3
import os, glob, requests, subprocess
from pathlib import Path
from dotenv import load_dotenv

load_dotenv("/workspace/.env")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
LUGANDA_REPO_URL = os.getenv("LUGANDA_REPO_URL", "https://github.com/MukalaziPatrick/Luganda_AI_Studio.git")
LUGANDA_LOCAL_PATH = os.getenv("LUGANDA_LOCAL_PATH", "/workspace/luganda-studio")
OLLAMA_URL = "http://localhost:11434/api/generate"
SKIP_DIRS = {".git", "__pycache__", "node_modules", "venv", ".venv", "dist", "build"}
REVIEW_EXTENSIONS = {".py", ".html", ".js", ".json"}
MAX_FILE_SIZE_KB = 100
DIVIDER = "━" * 60


def find_luganda_repo():
    if Path(LUGANDA_LOCAL_PATH).exists():
        print(f"✅ Found repo at {LUGANDA_LOCAL_PATH}")
        return Path(LUGANDA_LOCAL_PATH)
    candidates = glob.glob("/workspace/luganda*") + glob.glob("/workspace/Luganda*")
    for c in candidates:
        if Path(c).is_dir() and Path(c, "backend").exists():
            print(f"✅ Found repo at {c}")
            return Path(c)
    print(f"📥 Cloning from {LUGANDA_REPO_URL}")
    result = subprocess.run(["git", "clone", LUGANDA_REPO_URL, LUGANDA_LOCAL_PATH], capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Clone failed: {result.stderr}")
    print(f"✅ Cloned to {LUGANDA_LOCAL_PATH}")
    return Path(LUGANDA_LOCAL_PATH)


def collect_files(repo_path):
    files = []
    for ext in REVIEW_EXTENSIONS:
        for f in repo_path.rglob(f"*{ext}"):
            if any(part in SKIP_DIRS for part in f.parts):
                continue
            if f.stat().st_size > MAX_FILE_SIZE_KB * 1024:
                continue
            files.append(f)
    files.sort()
    return files


def ollama(model, prompt, timeout=180):
    try:
        resp = requests.post(OLLAMA_URL, json={"model": model, "prompt": prompt, "stream": False}, timeout=timeout)
        resp.raise_for_status()
        return resp.json().get("response", "").strip()
    except Exception as e:
        print(f"  ⚠️  Ollama error ({model}): {e}")
        return ""


def qwen_review_file(file_path, repo_path):
    relative = file_path.relative_to(repo_path)
    try:
        code = file_path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""
    prompt = f"""You are a senior software engineer reviewing code for a Luganda language learning app (FastAPI + ChromaDB backend).
Review this file and list ONLY real, specific issues. For each issue state the problem, show the exact fix, and rate confidence: HIGH/MEDIUM/LOW.
If the file looks fine respond with: NO_ISSUES

File: {relative}

```
{code[:6000]}
```

Issues:"""
    return ollama("qwen2.5-coder:32b", prompt)


def hermes_validate(file_path, repo_path, raw):
    if not raw or raw.strip() == "NO_ISSUES":
        return ""
    relative = file_path.relative_to(repo_path)
    prompt = f"""You are a senior engineer validating code review suggestions.
File: {relative}
Suggestions: {raw}
Keep only REAL issues. Format each as:
ISSUE: <description>
SUGGESTION: <fix>
CONFIDENCE: HIGH|MEDIUM|LOW
If none remain respond with: NO_ISSUES"""
    return ollama("hermes3:8b", prompt, timeout=120)


def send_telegram(token, chat_id, message):
    try:
        r = requests.post(f"https://api.telegram.org/bot{token}/sendMessage",
                          json={"chat_id": chat_id, "text": message}, timeout=15)
        print("📱 Telegram sent." if r.status_code == 200 else f"⚠️  Telegram failed: {r.text}")
    except Exception as e:
        print(f"⚠️  Telegram error: {e}")


if __name__ == "__main__":
    print("\n🔍 Luganda App Code Review Agent starting...")
    print("Models: hermes3:8b (orchestrator) + qwen2.5-coder:32b (reviewer)\n")
    repo = find_luganda_repo()
    files = collect_files(repo)
    print(f"📁 {len(files)} files to review\n")
    findings = []
    for i, fp in enumerate(files, 1):
        rel = fp.relative_to(repo)
        print(f"[{i}/{len(files)}] {rel} ...", end=" ", flush=True)
        raw = qwen_review_file(fp, repo)
        if not raw:
            print("⚠️  skipped")
            continue
        if raw.strip() == "NO_ISSUES":
            print("✅ clean")
            continue
        validated = hermes_validate(fp, repo, raw)
        if not validated or validated.strip() == "NO_ISSUES":
            print("✅ clean (validated)")
            continue
        print("🐛 issues found")
        print(f"\n{DIVIDER}\nFILE: {rel}\n{validated}\n{DIVIDER}")
        findings.append((fp, validated))
    high = sum(1 for _, v in findings if "CONFIDENCE: HIGH" in v)
    medium = sum(1 for _, v in findings if "CONFIDENCE: MEDIUM" in v)
    low = sum(1 for _, v in findings if "CONFIDENCE: LOW" in v)
    print(f"\n{'='*60}\n✅ Review complete\n📁 Files scanned: {len(files)}\n🐛 Issues in: {len(findings)} files\n   HIGH: {high}  MEDIUM: {medium}  LOW: {low}\n{'='*60}")
    if TELEGRAM_TOKEN:
        send_telegram(TELEGRAM_TOKEN, TELEGRAM_CHAT_ID,
                      f"✅ Luganda review done\n📁 {len(files)} files scanned\n🐛 {len(findings)} files with issues\n   HIGH:{high} MEDIUM:{medium} LOW:{low}\n👉 Check terminal")
