"""One-time startup check: seed the Railway volume's ChromaDB from the baked-in
seed_data/chromadb if the volume is empty. Railway volumes mount over /app/data,
shadowing anything committed under data/, so the real seed lives at seed_data/
(a path the volume does not shadow) and gets copied in on first boot only.
"""
import shutil
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SEED_CHROMA = BASE_DIR / "seed_data" / "chromadb"
LIVE_CHROMA = BASE_DIR / "data" / "chromadb"


def is_empty(chroma_path: Path) -> bool:
    sqlite_file = chroma_path / "chroma.sqlite3"
    if not sqlite_file.exists():
        return True
    try:
        import chromadb

        client = chromadb.PersistentClient(path=str(chroma_path))
        total = sum(client.get_collection(c.name).count() for c in client.list_collections())
        return total == 0
    except Exception as exc:
        print(f"[seed_volume_if_empty] could not inspect {chroma_path}: {exc}", file=sys.stderr)
        return False


def main() -> None:
    if not SEED_CHROMA.exists():
        print("[seed_volume_if_empty] no seed_data/chromadb in image, skipping")
        return

    if not is_empty(LIVE_CHROMA):
        print("[seed_volume_if_empty] live chromadb already has data, skipping seed")
        return

    print(f"[seed_volume_if_empty] live chromadb empty — seeding from {SEED_CHROMA}")
    LIVE_CHROMA.parent.mkdir(parents=True, exist_ok=True)
    if LIVE_CHROMA.exists():
        shutil.rmtree(LIVE_CHROMA)
    shutil.copytree(SEED_CHROMA, LIVE_CHROMA)
    print("[seed_volume_if_empty] seed complete")


if __name__ == "__main__":
    main()
