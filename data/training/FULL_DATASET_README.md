---
language:
- lug
- en
license: cc-by-4.0
task_categories:
- translation
- text-classification
tags:
- luganda
- english
- low-resource
- vocabulary
- grammar
pretty_name: Luganda-English Vocabulary, Sentence, Grammar, and Proverb Corpus
size_categories:
- n<1K
---

# Luganda ↔ English Vocabulary/Sentence/Grammar/Proverb Dataset

The curated corpus powering search and translation in
[Luganda AI Studio](https://github.com/MukalaziPatrick/luganda-ai-studio) —
vocabulary, example sentences, grammar rules, and traditional proverbs, each
human-verified by a native Luganda speaker.

## Dataset Description

Unlike the companion `luganda-en-dataset` (user-submitted correction pairs),
this dataset is the original curated reference corpus: dictionary-style
vocabulary entries, everyday sentence pairs, grammar rule explanations, and
Kiganda proverbs with their meanings.

## Schema

| Column | Type | Description |
|---|---|---|
| luganda | string | Luganda text |
| english | string | English text |
| type | string | `vocabulary`, `sentence`, `grammar`, or `proverb` |
| category | string | Source category, e.g. `animals`, `grammar_verb_tenses` |
| notes | string or null | Additional context: word meaning, proverb theme, or grammar rule explanation |

## Usage

```python
from datasets import load_dataset

ds = load_dataset("Mukalazipatrick/luganda-vocabulary-dataset")
```

## License

CC BY 4.0 — Free to use with attribution.
