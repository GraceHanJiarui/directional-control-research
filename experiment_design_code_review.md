# Experiment Design And Code Review

This note records a focused review of the current experiment design and code, with special attention to the two recent negative high-level direction attempts:

- `affect_attuned vs affect_flat`
- `deferential_uncertain vs decisive_direct`

The goal is narrow:
- distinguish real design limitations from implementation bugs;
- confirm whether the retained core evidence still stands;
- and clarify what likely caused the recent negative explorations to fail.

## Executive Verdict

Current verdict:
- no newly found code issue appears to invalidate the retained core mainline claims;
- the strongest retained results remain technically credible under the current narrowed wording;
- the failed `affect` and `stance` lines look more like **axis-design / data-geometry failures** than hidden training-pipeline corruption.

In other words:
- the training system itself was not the main reason those two axes failed;
- the mainline anti-underanswer results should still be treated as valid retained evidence;
- but the current compact stage-2 framework is not strong at turning arbitrary high-level directions into clean, stable policy axes.

## What Was A Real Training / Infrastructure Problem

There were real infrastructure issues earlier, and they mattered:

1. Windows JSON loading instability in DPO training
- old DPO training could hang inside `datasets.load_dataset("json", ...)`
- this was a real training-entry problem, not a model behavior signal

Current status:
- fixed in `directional_control_research/mechanism_experiment/scripts/train_dpo_mechanism.py`
- the loader now uses local JSONL reading plus local tokenization

2. Preference-pair anchor inconsistency
- earlier non-baseline DPO pairs were sometimes built under `BASELINE_SYSTEM` even when the initialized policy was `anti` or `minimal`
- this was a real objective mismatch

Current status:
- fixed in the cleaner `v2` reversal rebuilds

3. Broken `one_layer` pair construction
- after sentence splitting was corrected, the old `one_layer` construction no longer yielded valid usable samples
- so the earlier `minimal -> one_layer` line should not be treated as real evidence

Current status:
- excluded from retained evidence

These were real issues.
They explain part of the earlier noise, but they do **not** explain away the retained mainline.

## Review Of The Retained Mainline Pipeline

### SFT training path

Main script:
- `directional_control_research/mechanism_experiment/scripts/train_qlora_mechanism.py`

Current review result:
- the current SFT path is structurally standard and coherent:
  - local JSONL row loading;
  - message rendering through `render_chat(...)`;
  - prompt masking with `-100`;
  - assistant-token cross-entropy training;
  - optional prefix / suffix / EOS supervision;
  - LoRA target-module selection by model family.

No newly found issue here currently suggests that:
- `baseline / anti / minimal`
- `anti_prefix50 / true_eos / tailspan`
- `baseline_then_anti_stage2`

were artifacts of a broken SFT trainer.

### Evaluation path

The core retained eval scripts remain:
- `eval_lora_adapter.py`
- `eval_lora_adapter_phase2.py`
- `eval_forced_prefix_continuation.py`
- `eval_asymmetric_controllability_matrix.py`
- `eval_uncertainty_probe.py`
- `eval_compression_vs_pruning_probe.py`

Current interpretation boundary remains the same:
- exact character counts should not be over-read in isolation;
- the stronger evidence comes from convergence across:
  - Phase 2,
  - forced-prefix,
  - asymmetric controllability,
  - compression-vs-pruning,
  - stage split.

No newly found issue in these scripts currently forces withdrawal of the retained claims.

## Review Of The Additional High-Level Direction Attempts

## 1. Affect axis

Relevant generators / builders:
- `scripts/generate_affect_axis_v1_triplets.py`
- `scripts/generate_affect_axis_v2_triplets.py`
- `scripts/generate_affect_axis_v3_triplets.py`
- `scripts/build_affect_triplet_sft_datasets.py`

### What looks technically fine

- the builder itself is straightforward:
  - one system prompt per variant;
  - one user message;
  - one assistant target;
  - same JSONL packaging as the mainline
- later rebuilds were not blocked by the old JSON loader problem
- stage-2 training ran successfully and smoke checkpoints were usable

### What looks weak in the design

1. The axis is semantically thin
- `affect_attuned` was intended to differ from `flat` mainly by a brief emotional acknowledgment
- that difference is small relative to the overall answer distribution

2. The axis easily collapses into nearby bundled behaviors
- comfort scripting
- extra support
- extra warmth
- extra interaction
- longer answers

3. The compact source manifold is narrow
- the affect-specific rebuilds used only a handful of emotional cases
- wrappers and body builders expand them, but they do not create genuinely broad supervision diversity

### Review conclusion on affect

The affect line does **not** currently look like a hidden code bug.
It looks like:
- a supervision axis that is too soft,
- too easily confounded with nearby interpersonal/helpfulness behaviors,
- and too narrow in source-case coverage to stabilize as a clean stage-2 policy direction.

## 2. Stance axis

Relevant generators / builders:
- `scripts/generate_stance_axis_v1_triplets.py`
- `scripts/build_stance_triplet_sft_datasets.py`
- `data/stance_controllability_matrix_v1.json`

### What looks technically fine

- the dataset structure is coherent;
- the targets were intentionally designed to keep core answer content similar while changing stance;
- training completed on GPU without instability;
- smoke outputs were usable.

### What looks weak in the design

1. Baseline prompt steering already moves the axis strongly
- this means the axis may be too prompt-legible and too weakly policy-specific
- a stage-2 update then has less room to create a distinctive sticky family

2. The target distinction is still not fully disentangled
- `deferential` tends to be longer and more conditional
- `decisive` tends to be shorter and more forceful
- so stance still carries residual coupling to:
  - length,
  - certainty,
  - and sometimes content framing

3. The training manifold is still small
- only `18` source cases, expanded by wrappers
- this is broader than affect `v3`, but still narrow for a subtle high-level stance axis

### Review conclusion on stance

The stance line also does **not** primarily look like hidden pipeline corruption.
It looks like:
- a real but fragile axis,
- partly steerable already at prompt time,
- and not strongly enough separated from length/content framing to survive stage-2 consolidation cleanly.

## Main Design Limitation Behind Both Negative Lines

The same structural limitation appears in both failures:

### The current stage-2 framework is strongest when the target direction is:
- behaviorally thick,
- repeatedly expressed across many contexts,
- and tightly coupled to content-budgeting choices.

`anti_underanswer` satisfies that unusually well.

By contrast:
- `affect_attuned`
- `affect_flat`
- `deferential_uncertain`
- `decisive_direct`

are all:
- higher-level,
- semantically thinner,
- and easier to absorb into nearby bundled behaviors rather than stabilize as a single family direction.

So the negative results are meaningful:
- they do not show the framework is invalid;
- they show the framework has limited power for subtle high-level axis induction.

## Residual Risks That Still Exist

The following are still real boundaries, even if they are not fatal bugs:

1. Compact source-case coverage
- many lines still depend on a small number of canonical source cases expanded by wrappers
- this is efficient for mechanism probing but weak for broad style induction

2. High-level target entanglement
- even "same-content" targets can still differ in:
  - sentence count,
  - answer confidence,
  - interaction style,
  - and help expansion

3. Stage-2 family induction is easier for broad policy bundles than for subtle axes
- the framework currently favors thicker directional families

## Practical Interpretation

The current clean reading is:

- the mainline retained anti-underanswer results remain valid;
- earlier DPO/reversal bugs were real and have already been corrected where it mattered;
- the recent `affect` and `stance` failures do not currently justify saying the whole experiment is flawed;
- they do justify saying that:
  - the compact stage-2 setup is poor at producing a second clean high-level control axis,
  - and that the over-expansion line remains unusually special inside this framework.

## What To Say In The Paper

Safe wording:
- additional high-level contrastive directions were attempted and trained successfully;
- however, they did not yield clean retained axes under fuller evaluation;
- this narrows the current generality claim rather than invalidating the mainline.

Unsafe wording:
- that no other high-level sticky direction exists;
- or that the whole framework is generally invalid.

## Recommended Next Move

At this point the best use of effort is:

1. keep the retained anti-underanswer mainline;
2. treat `affect` and `stance` as negative exploration;
3. stop using new high-level stage-2 lines as the main path to stronger claims unless the data regime becomes much larger and more targeted.

## Addendum: `caveat` as a partial extension

Subsequent work added a more targeted high-level line:
- `caveat / completeness`

Review conclusion on that extension:
- the external benchmark result was real;
- the controlled-family follow-up was not empty;
- but the family did not become a second fully clean retained axis.

More specifically:
- `caveat_v1` was too bundled;
- `caveat_v2` became materially cleaner;
- `caveat_v3` did not improve further.

So the current design lesson is sharper than before:
- the framework can partially isolate a second member of the same broad "too-much assistant" cluster;
- but outside the main anti-underanswer line, the compact family setup still struggles to turn neighboring high-level tendencies into equally clean retained stage-2 directions.

Practical implication:
- if one more controlled-family experiment is still desired, `next_step` is the only clearly motivated candidate left;
- otherwise, the current evidence base is already coherent enough to stop experimentation and write the paper with honest boundaries.
