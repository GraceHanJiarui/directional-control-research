# Cross-Over Reversal Diagnosis

This note records the current diagnosis of the two cross-over reversal runs:

- `anti_underanswer_sft_v5 -> preference_minimal`
- `minimal_boundary_sft_v5 -> preference_expand`

The goal is to separate:
- a real retained later-stage reversal result,
- from a noisy opposite-direction run that should not currently be retained as evidence.

## Main result

The two reversal directions do **not** behave symmetrically.

### Retained result

`anti_underanswer_sft_v5 -> preference_minimal` is a real retained reversal line.

Evidence:
- Phase 2 means fall from direct anti:
  - `neutral`: `34.42 -> 14.5`
  - `avoid_underanswer`: `51.17 -> 22.75`
  - `scope_minimal_sufficient`: `32.25 -> 19.67`
  - `do_not_add_unasked_help`: `47.58 -> 23.0`
- Forced-prefix continuation collapses:
  - direct anti: strong continuation regime
  - reversal line: `8/12` immediate stops, `mean continuation chars = 4.33`
- Asymmetric controllability flattens sharply:
  - direct anti:
    - `scope delta = -12.67`
    - `interaction delta = -47.83`
    - `help delta = +18.83`
  - anti-to-minimal reversal:
    - `scope delta = +11.33`
    - `interaction delta = +0.67`
    - `help delta = +4.67`

Interpretation:
- later preference-like optimization is capable, in at least one important direction, of meaningfully pulling back an already sticky anti-oriented SFT policy;
- this is stronger than same-direction amplification alone.

## Failed opposite-direction reversal

`minimal_boundary_sft_v5 -> preference_expand` is **not** currently a retained result.

### Why it is not retained

The issue is not numerical collapse.
Training is stable and smoke output is readable.
The failure appears in fuller evaluation.

Evidence:
- Phase 2 means jump far beyond direct minimal:
  - `neutral`: `17.25 -> 60.5`
  - `avoid_underanswer`: `20.17 -> 71.0`
  - `scope_minimal_sufficient`: `14.75 -> 99.0`
  - `do_not_add_unasked_help`: `39.17 -> 67.5`
- Forced-prefix becomes heavily continuation-prone:
  - `10/12` continuations
  - `mean continuation chars = 43.5`
- Asymmetric controllability becomes distorted rather than cleanly expand-like:
  - direct minimal:
    - `scope delta = +7.0`
    - `interaction delta = +1.83`
    - `help delta = +6.17`
  - minimal-to-expand reversal:
    - `scope delta = -9.0`
    - `interaction delta = -43.83`
    - `help delta = +59.17`

### What the outputs look like

The strongest warning sign is not only longer outputs.
It is **boundary distortion**.

Example failure patterns:
- under `scope_minimal_sufficient`, the model may start answering and then drift into a new scenario or a much broader explanatory branch;
- under asymmetric control, even `ask_minimal` can include extra help, follow-up offers, or soft-closure boilerplate;
- some examples look like the model is satisfying the preference by becoming generically more expansive, rather than cleanly adding one more useful layer.

This means the line behaves more like a dirty bundled shift than a crisp interpretable reversal.

## Current diagnosis

The simplest current diagnosis is:

1. `anti -> preference_minimal` is a **shorter, cleaner pullback target**.
2. `minimal -> preference_expand` is a **much larger jump** into a bundled target space.

### Evidence from pair construction

The current pair files use:
- for anti-to-minimal:
  - `chosen = minimal_boundary_response`
  - `rejected = anti_underanswer_response`
- for minimal-to-expand:
  - `chosen = anti_underanswer_response`
  - `rejected = minimal_boundary_response`

On the current `medium160` pair files:
- anti-to-minimal:
  - `chosen_mean = 26.14`
  - `rejected_mean = 91.92`
- minimal-to-expand:
  - `chosen_mean = 91.92`
  - `rejected_mean = 26.14`

So the expand reversal is not asking for a mild one-level expansion.
It is asking a narrow policy to jump directly into a much more bundled, much longer anti-style target regime.

### Why that likely matters

For the failed direction, the optimizer can satisfy the preference in many messy ways:
- add generic explanation;
- add proactive next-step help;
- add follow-up offers;
- broaden the task framing;
- or drift into a more globally talkative assistant behavior.

That is consistent with what appears in the fuller eval outputs.

## Most likely causes of the failed `minimal -> preference_expand` line

### 1. Target jump is too large

The chosen answers are full anti-style responses, not gentle one-level expansions over minimal.
So the optimization target is broad and bundled from the start.

### 2. The target direction is bundled, not local

The model is not learning "expand one level" as a clean axis.
It is being pulled toward a whole anti-style bundle:
- more content,
- more help,
- more continuation,
- more assistant-forward behavior.

### 3. The current preference prompt anchor is neutral

The pair-generation script uses the baseline assistant system prompt as the prompt anchor.
That means the preference stage is not explicitly constrained to realize the expansion in a narrow or axis-local way.

### 4. Narrow-policy initialization may make the jump more brittle

The run starts from `minimal_boundary_sft_v5` and references `minimal_boundary_sft_v5`.
That makes the preference update a large departure from the current policy manifold, which may encourage unstable bundled drift rather than a clean local expansion.

## What to do next

### Highest-value next step on the retained line

Deepen `anti -> preference_minimal`.

Best follow-ups:
- run a small strength sweep around the current retained medium setting:
  - vary pair count moderately;
  - vary `beta` or `num_epochs` conservatively;
- report per-case paired deltas against direct anti;
- add bundled-generalization eval on this reversal line, not only Phase 2 / forced-prefix / asymmetric.

### Best diagnosis path for the failed line

Do **not** just scale the same `minimal -> anti-style` preference pairs.

Instead, test progressively softer expansion targets:

1. `minimal -> preference_baseline`
- `chosen = baseline_response`
- `rejected = minimal_boundary_response`
- asks whether a narrow policy can be pulled back to the middle cleanly.

2. filtered `minimal -> preference_expand_soft`
- keep `chosen = anti_underanswer_response`
- but only on items where the anti/minimal length ratio is moderate;
- avoid the most aggressively bundled anti targets.

3. category-restricted expand reversal
- first test only `task_primary`
- then add `practical_troubleshooting`
- leave `clarify_next_step` and `low_support_presence` for later if they prove to be the main source of bundle drift.

## Bottom line

The current reversal evidence should be read as:

- later preference-like optimization can genuinely pull back a sticky anti SFT policy;
- this is real and important;
- but the reverse direction is not yet clean, and its failure currently looks more like bundled-target instability than a simple absence of reversal capacity.
