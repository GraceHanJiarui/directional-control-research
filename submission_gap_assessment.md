# Submission Gap Assessment

This note answers a narrow question: given the current retained evidence base, what submission tier is realistic, what gaps still block a strong main-track claim, and what should be added next.

## Current assessment

### Not strong enough yet for a confident top-main submission

As the project stands, the evidence is **not yet strong enough for a confident top-main submission** in a highly selective main track.

The main reasons are structural rather than cosmetic:

1. Stage-split evidence is strong for same-direction amplification, and now materially strengthened for reversal, but still incomplete:
   - `baseline -> anti stage2` is strong;
   - `baseline -> preference_expand` is usable;
   - cleaner `v2` evaluation confirms `anti_underanswer_sft_v5 -> preference_minimal` as a strong retained reversal result;
   - cleaner `v2` evaluation gives a weaker partial midpoint pullback on the minimal side;
   - there is still no symmetric clean outward-from-minimal reversal result.

2. The generality claim is still narrower than a strong main-track mechanism paper usually wants:
   - the main Chinese line is concentrated in one primary family;
   - the SmolLM2 replication is useful, but it changes both family and language at once;
   - beyond `emoji_only`, we still lack a second clean retained high-level SFT direction.

3. The project currently has a strong behavioral-mechanism story, but not a very broad scaling or large-model story.
   - That does not invalidate the work.
   - It does narrow the realistic venue target.

## What would most improve paper strength

### Priority 1: present the completed planning-vs-stopping decomposition cleanly

This gap is now materially closed at the annotation level.

What now exists:
- a completed focused `v2` label pack over `80` rows;
- model- and mode-level summaries;
- quantitative support for a mixed mechanism picture.

Most important result:
- `scope_minimal_sufficient` is relatively more planning-sensitive;
- `do_not_add_unasked_help` is strongly stopping-dominated.

Why this still matters for submission:
- the paper should now elevate these numbers into the main results section rather than still describing them as future work.

### Priority 2: consolidate and present the reversal evidence cleanly

What changed:
- we now have one strong retained reversal result:
  - `anti_underanswer_sft_v5 -> preference_minimal` (`v2`)
- and one weaker partial midpoint pullback:
  - `minimal_boundary_sft_v5 -> preference_baseline_task_primary_minanchor` (`v2`)
- but still not a symmetric opposite-direction clean reversal.

What to do next:
- report paired per-case deltas against direct `anti_underanswer_sft_v5`;
- add bundled-generalization evaluation on the retained anti-to-minimal reversal;
- complete the writeup of the cleaner v2 rebuild so reviewers can see that the asymmetry survives pair-design and training-entry fixes.

Why this matters:
- the paper now has real reversal evidence plus a weaker opposite-side midpoint result, which is a substantial upgrade;
- but it still cannot claim that later preference-like stages can symmetrically rewrite any already-shaped sticky SFT policy.

### Priority 3: add one additional clean high-level direction

The current retained contrast is:
- shallow control: `emoji_only`
- high-level mainline: `anti_underanswer`

What is missing:
- at least one more clean retained high-level SFT direction that survives smoke and fuller evaluation.

What has now been tried and not retained:
- `affect_attuned vs affect_flat`
- `deferential_uncertain vs decisive_direct`

What that changes:
- the generality gap is still real;
- but the project can now honestly say it attempted additional high-level directions and did not find a second clean retained axis inside the current compact stage-2 framework.
- this supports a narrower comparative reading:
  - `anti_underanswer / over-expansion` currently looks more special than generic,
  - even if the paper still should not overclaim absolute uniqueness.

Why this matters:
- without it, the paper cannot yet say whether hard suppressibility is specific to over-expansion or reflects a broader class of high-level SFT-stabilized assistant-policy biases.

### Updated status after the external multi-axis cluster benchmark and caveat family

This gap is now narrower, but not fully closed.

What now exists:
- aligned external multi-axis evidence across multiple strong-model settings;
- a stronger external cluster picture centered on:
  - `caveat / completeness`
  - `next_step / proactivity`
  - weaker `moralizing / residual normative framing`
- a controlled-family extension on `caveat`.

What the `caveat` extension established:
- `caveat_v1`: clear signal, but heavily bundled;
- `caveat_v2`: materially cleaner and the best current version;
- `caveat_v3`: targeted positive-side patching did not improve the family further.

Current interpretation:
- this is stronger than pure external pattern matching;
- but it is still only **partial controlled-family evidence**, not a second retained clean direction.

Submission implication:
- the paper can now say more than "only the length axis mattered";
- but it still should not claim that a second high-level SFT family has been cleanly established at the same level as `anti_underanswer`.

### Priority 4: strengthen statistical presentation

Even if the raw conclusions do not change, the paper will read as more mature if the main retained comparisons are accompanied by:
- per-case paired deltas,
- bootstrap confidence intervals or simple paired resampling,
- a compact table of retained-vs-excluded lines and why exclusions occurred.

This is not the highest scientific gap, but it matters for review confidence.

## Realistic venue guidance

### Current state, without new supplementation

Realistic:
- strong workshop paper;
- reasonable Findings-level target if the paper is written tightly and boundaries are stated honestly.

Ambitious but low-confidence:
- top main track.

### If Priority 1 + Priority 2 are completed cleanly

The paper becomes materially stronger.

At that point, a more realistic target becomes:
- a serious Findings submission;
- a more defensible main-track long-shot if the writing is excellent and the claims stay narrow.

### If Priority 1 + Priority 2 + Priority 3 all land cleanly

That would be the first point where a top-main attempt becomes technically more defensible.

Even then, the paper would still be stronger as:
- a carefully framed behavioral-mechanism paper,
- not a broad universal claim about all post-training pipelines.

## Practical next move

The highest-yield order is:

1. package the completed planning-vs-stopping decomposition cleanly in the paper;
2. package the cleaner `v2` reversal evidence cleanly, especially the retained anti-to-minimal line and the weaker minimal-side midpoint pullback;
3. decide whether one more clean high-level direction is feasible within remaining time.

Current recommendation:
- for the paper as it stands, further small repairs on `caveat` are likely low-yield;
- `next_step` is the only additional controlled-family line that still looks technically worth trying if one more experiment is desired;
- but it should be treated as an optional last attempt, not as a remaining requirement for writing.

## New scaffolding added now

To reduce restart cost, cross-over reversal preference-stage scaffolding now exists for:

- `minimal_then_preference_expand_stage3_gpu_medium_v1_1p5b`
- `anti_then_preference_minimal_stage3_gpu_medium_v1_1p5b`

with matching pair-generation support under:
- `directional_control_research/mechanism_experiment/scripts/generate_preference_pairs_cross_reversal_v1.py`

and generated-pair targets expected under:
- `directional_control_research/mechanism_experiment/data/built_pref_v1`

Current outcome:
- the scaffolding produced one retained reversal result (`anti -> preference_minimal`);
- the opposite-direction run did not yet land as a clean retained line.

Submission implication:
- this is a real upgrade over the previous state;
- it likely strengthens the paper from "strong workshop / Findings" toward "stronger Findings and better main-track long-shot";
- but by itself it still does not close the remaining main-track gaps.
