# Mechanism Experiment Data

This directory contains:
- clean held-out evaluation sets
- retained training sources
- derived training datasets for specific mechanism probes
- lightweight templates and notes

## Canonical retained source

The current retained source triplets are:
- `train_triplets_v5_clean_240.jsonl`

These source rows are converted into built datasets under:
- `built_v5/`
- `built_q3/`
- `built_q4/`

## Template file

`train_triplets_template.jsonl` is only a human-readable template.
It is not part of the active training pipeline and should not be treated as a canonical source.

## Built training row format

Each built JSONL row has the form:

```json
{
  "messages": [
    {"role": "system", "content": "<system prompt>"},
    {"role": "user", "content": "<user text>"},
    {"role": "assistant", "content": "<target response>"}
  ],
  "example_id": "...",
  "language": "zh",
  "category": "task_primary",
  "target_style": "baseline_sft"
}
```
