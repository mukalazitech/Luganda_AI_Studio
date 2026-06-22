# scripts/finetune_lora.py

"""
LoRA fine-tuning script for NLLB-200-distilled-600M on Luganda ↔ English.

REQUIREMENTS:
  pip install peft transformers datasets accelerate bitsandbytes

HARDWARE:
  - Minimum: CPU (slow, ~hours per epoch)
  - Recommended: NVIDIA RTX 3050 4 GB VRAM (this machine)
  - Model is loaded in 8-bit quantisation via bitsandbytes to fit in 4 GB VRAM

USAGE:
  # Check you have enough pairs first
  python scripts/finetune_lora.py --check

  # Dry-run (validates data, prints config, does NOT train)
  python scripts/finetune_lora.py --dry-run

  # Train
  python scripts/finetune_lora.py

  # Train with custom output dir and epochs
  python scripts/finetune_lora.py --output-dir data/lora/run2 --epochs 5

MINIMUM PAIRS:
  500 verified correction pairs recommended before running.
  The script will warn (and abort unless --force is passed) below this threshold.

OUTPUT:
  data/lora/YYYY-MM-DD/
    adapter_model.bin       ← LoRA adapter weights (small, ~10 MB)
    adapter_config.json     ← PEFT config
    training_log.jsonl      ← Loss per step

AFTER TRAINING:
  Load the adapter at inference time via peft.PeftModel:

    from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
    from peft import PeftModel

    base = AutoModelForSeq2SeqLM.from_pretrained("facebook/nllb-200-distilled-600M")
    model = PeftModel.from_pretrained(base, "data/lora/YYYY-MM-DD")
"""

import argparse
import json
import logging
import sys
from datetime import date
from pathlib import Path
from typing import Optional

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

EXPORT_DIR       = PROJECT_ROOT / "data" / "training"
DEFAULT_OUT_DIR  = PROJECT_ROOT / "data" / "lora" / date.today().isoformat()
BASE_MODEL       = "facebook/nllb-200-distilled-600M"
MIN_PAIRS        = 500

# NLLB language codes
LANG_CODES = {
    "en_to_lg": ("eng_Latn", "lug_Latn"),
    "lg_to_en": ("lug_Latn", "eng_Latn"),
}

# LoRA config — conservative for 4 GB VRAM
LORA_CONFIG = {
    "r": 8,
    "lora_alpha": 16,
    "lora_dropout": 0.05,
    "bias": "none",
    "task_type": "SEQ_2_SEQ_LM",
    "target_modules": ["q_proj", "v_proj"],
}

TRAIN_CONFIG = {
    "num_epochs": 3,
    "batch_size": 4,
    "gradient_accumulation_steps": 4,   # effective batch = 16
    "learning_rate": 3e-4,
    "max_source_length": 128,
    "max_target_length": 128,
    "warmup_steps": 50,
    "logging_steps": 10,
    "save_steps": 100,
    "fp16": True,                        # requires CUDA; set False for CPU
}


# ── Data loading ──────────────────────────────────────────────────────────────

def _load_export_pairs() -> list[dict]:
    """
    Load the most recent dataset_export_*.jsonl file.
    Only returns verified=True pairs — unverified pairs are excluded from LoRA training
    because they may contain noise from the NLLB model itself.
    """
    exports = sorted(EXPORT_DIR.glob("dataset_export_*.jsonl"))
    if not exports:
        return []
    path = exports[-1]
    logger.info(f"Loading export: {path.name}")
    records = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
                if r.get("verified"):
                    records.append(r)
            except json.JSONDecodeError:
                pass
    return records


def _check_pairs(pairs: list[dict], force: bool) -> None:
    n = len(pairs)
    logger.info(f"Verified pairs available: {n}")
    if n < MIN_PAIRS:
        msg = (
            f"Only {n} verified pairs found. "
            f"Minimum recommended is {MIN_PAIRS}. "
            f"Fine-tuning on fewer pairs risks overfitting. "
        )
        if force:
            logger.warning(msg + "Proceeding because --force was passed.")
        else:
            logger.error(msg + "Run with --force to override, or collect more corrections first.")
            sys.exit(1)


# ── Training ──────────────────────────────────────────────────────────────────

def _train(pairs: list[dict], output_dir: Path, epochs: int, dry_run: bool) -> None:
    """
    Fine-tune NLLB-200-distilled-600M with LoRA on the provided pairs.
    """
    try:
        import torch
        from transformers import (
            AutoTokenizer,
            AutoModelForSeq2SeqLM,
            Seq2SeqTrainer,
            Seq2SeqTrainingArguments,
            DataCollatorForSeq2Seq,
        )
        from peft import LoraConfig, get_peft_model, TaskType
        from datasets import Dataset
    except ImportError as e:
        logger.error(
            f"Missing dependency: {e}\n"
            "Install with: pip install peft transformers datasets accelerate bitsandbytes"
        )
        sys.exit(1)

    use_cuda = torch.cuda.is_available()
    logger.info(f"CUDA available: {use_cuda}")
    if not use_cuda:
        logger.warning("No GPU detected. Training will be very slow on CPU.")
        TRAIN_CONFIG["fp16"] = False

    # ── Load tokenizer + model ────────────────────────────────────────────────
    logger.info(f"Loading tokenizer: {BASE_MODEL}")
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)

    load_kwargs = {}
    if use_cuda:
        try:
            load_kwargs = {"load_in_8bit": True, "device_map": "auto"}
            logger.info("Loading model in 8-bit quantisation (4 GB VRAM mode)")
        except Exception:
            load_kwargs = {}
            logger.warning("8-bit loading failed — falling back to full precision")

    logger.info(f"Loading base model: {BASE_MODEL}")
    model = AutoModelForSeq2SeqLM.from_pretrained(BASE_MODEL, **load_kwargs)

    # ── Apply LoRA ────────────────────────────────────────────────────────────
    lora_cfg = LoraConfig(
        r=LORA_CONFIG["r"],
        lora_alpha=LORA_CONFIG["lora_alpha"],
        lora_dropout=LORA_CONFIG["lora_dropout"],
        bias=LORA_CONFIG["bias"],
        task_type=TaskType.SEQ_2_SEQ_LM,
        target_modules=LORA_CONFIG["target_modules"],
    )
    model = get_peft_model(model, lora_cfg)
    model.print_trainable_parameters()

    if dry_run:
        logger.info("[DRY RUN] Model + LoRA loaded successfully. Skipping training.")
        return

    # ── Build dataset ─────────────────────────────────────────────────────────
    def _make_hf_dataset(pairs: list[dict]) -> Dataset:
        rows = {"input_text": [], "target_text": [], "src_lang": [], "tgt_lang": []}
        for p in pairs:
            direction = p.get("direction", "en_to_lg")
            src_lang, tgt_lang = LANG_CODES.get(direction, ("eng_Latn", "lug_Latn"))
            rows["input_text"].append(p["source"])
            rows["target_text"].append(p["target"])
            rows["src_lang"].append(src_lang)
            rows["tgt_lang"].append(tgt_lang)
        return Dataset.from_dict(rows)

    def _tokenize(batch):
        tokenizer.src_lang = batch["src_lang"][0]
        model_inputs = tokenizer(
            batch["input_text"],
            max_length=TRAIN_CONFIG["max_source_length"],
            truncation=True,
            padding="max_length",
        )
        target_lang_code = batch["tgt_lang"][0]
        with tokenizer.as_target_tokenizer():
            labels = tokenizer(
                batch["target_text"],
                max_length=TRAIN_CONFIG["max_target_length"],
                truncation=True,
                padding="max_length",
            )
        model_inputs["labels"] = labels["input_ids"]
        return model_inputs

    hf_ds = _make_hf_dataset(pairs)
    split = hf_ds.train_test_split(test_size=min(0.1, 50 / len(pairs)), seed=42)
    tokenized = split.map(_tokenize, batched=True, batch_size=32, remove_columns=hf_ds.column_names)

    # ── Training arguments ────────────────────────────────────────────────────
    output_dir.mkdir(parents=True, exist_ok=True)
    training_args = Seq2SeqTrainingArguments(
        output_dir=str(output_dir),
        num_train_epochs=epochs,
        per_device_train_batch_size=TRAIN_CONFIG["batch_size"],
        gradient_accumulation_steps=TRAIN_CONFIG["gradient_accumulation_steps"],
        learning_rate=TRAIN_CONFIG["learning_rate"],
        warmup_steps=TRAIN_CONFIG["warmup_steps"],
        fp16=TRAIN_CONFIG["fp16"],
        logging_steps=TRAIN_CONFIG["logging_steps"],
        save_steps=TRAIN_CONFIG["save_steps"],
        evaluation_strategy="epoch",
        predict_with_generate=True,
        report_to="none",
    )

    data_collator = DataCollatorForSeq2Seq(tokenizer, model=model, padding=True)

    trainer = Seq2SeqTrainer(
        model=model,
        args=training_args,
        train_dataset=tokenized["train"],
        eval_dataset=tokenized["test"],
        tokenizer=tokenizer,
        data_collator=data_collator,
    )

    logger.info(f"Starting training — {len(tokenized['train'])} train, {len(tokenized['test'])} eval")
    trainer.train()

    # ── Save LoRA adapter only (not the full model) ────────────────────────────
    model.save_pretrained(str(output_dir))
    tokenizer.save_pretrained(str(output_dir))
    logger.info(f"LoRA adapter saved to: {output_dir}")


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="LoRA fine-tune NLLB-200 on Luganda corrections")
    parser.add_argument("--check", action="store_true", help="Count available pairs and exit")
    parser.add_argument("--dry-run", action="store_true", help="Load model + data but do not train")
    parser.add_argument("--force", action="store_true", help=f"Train even if fewer than {MIN_PAIRS} pairs")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUT_DIR, help="Where to save the adapter")
    parser.add_argument("--epochs", type=int, default=TRAIN_CONFIG["num_epochs"], help="Number of training epochs")
    args = parser.parse_args()

    pairs = _load_export_pairs()

    if args.check:
        logger.info(f"Verified pairs available: {len(pairs)}")
        logger.info(f"Minimum recommended:      {MIN_PAIRS}")
        if len(pairs) >= MIN_PAIRS:
            logger.info("Ready to train.")
        else:
            logger.warning(f"Need {MIN_PAIRS - len(pairs)} more pairs before training.")
        return

    _check_pairs(pairs, force=args.force)

    logger.info(f"Output directory: {args.output_dir}")
    logger.info(f"Epochs: {args.epochs}")

    _train(pairs, output_dir=args.output_dir, epochs=args.epochs, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
