# Mechanism Experiment Failure Log

Date: 2026-03-26

## Kept
- v5 clean source triplets: `data/train_triplets_v5_clean_240.jsonl`
- v5 built datasets: `data/built_v5/`
- v5 configs: `configs/*_sft_v5.yaml`
- v5 baseline adapter: `outputs/qwen25_1p5b_baseline_sft_v5/`
- current scripts and docs under `scripts/` and `docs/`

## Invalidated / deleted

### v3
- `data/train_triplets_v3_216.jsonl`
- `data/built_v3/`
- `configs/*_sft_v3.yaml`
- `outputs/qwen25_1p5b_*_sft_v3/`
- `outputs/qwen25_1p5b_baseline_sft_v3_eval.jsonl`

Reason:
- training targets came directly from earlier Qwen experiment outputs
- eval showed boundary-text leakage and repetition
- not usable for mechanism interpretation

### v4
- `data/train_triplets_v4_432.jsonl`
- `data/built_v4/`
- `configs/*_sft_v4.yaml`
- `outputs/qwen25_1p5b_*_sft_v4/`
- `outputs/qwen25_1p5b_baseline_sft_v4_eval.jsonl`

Reason:
- input-side boundary serialization was improved relative to v3
- but target-side distribution remained polluted
- held-out baseline eval produced continuation artifacts (`GuidId`, `_Pods`, pseudo multi-turn self-dialogue)
- not usable for mechanism interpretation

### older intermediate sets
- `data/train_triplets_v1_240.jsonl`
- `data/train_triplets_v2_216.jsonl`
- `data/built_v2/`
- `configs/baseline_sft_v2.yaml`
- `configs/anti_underanswer_sft_v2.yaml`
- `configs/minimal_boundary_sft_v2.yaml`

Reason:
- superseded by later iterations and not part of retained clean pipeline

## Current blocker
- HF-based local eval on this Windows environment remains unstable and can segfault
- until eval path is replaced or stabilized, only adapter training outputs should be trusted

## Current active line
- Train/evaluate only on `v5 clean`
- Do not reuse old v3/v4 outputs or datasets

## 2026-03-30 cleanup update

### Invalidated / abandoned due to corrupted local artifacts
- `data/branchpoint_probe_v1.json`
- `tmp_chinese_probe.txt`
- `scripts/eval_branchpoint_probe.py`
- `scripts/summarize_branchpoint_probe.py`

Reason:
- the manually written branchpoint probe spec was actually saved with literal `?` corruption in file contents;
- the branchpoint line was abandoned before being used as retained evidence.

Effect on retained results:
- no retained Q1/Q2/Q3/Q4 claim depends on this branchpoint line;
- no rerun is required for the retained mainline because this probe was not used as accepted evidence.

### Clarify-first family caution
- `scripts/generate_clarify_first_v1_dataset.py` had punctuation corruption (`?` collapsed to `?` in the generator logic)
- `data/built_q3/clarify_first_sft_v1_train.jsonl` has been regenerated with corrected punctuation handling

Effect on retained results:
- `clarify_first_sft_v1` should be treated as exploratory / inconclusive rather than as strong retained evidence;
- if we want to use a clarify-family result later, it should be retrained and reevaluated from the regenerated dataset.
