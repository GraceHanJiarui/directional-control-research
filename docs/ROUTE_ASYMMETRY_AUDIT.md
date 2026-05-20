# Route Asymmetry Audit

Scope:
- Source files inspected:
  - `app/generation/actor_prompt.py`
  - `app/generation/execution_interface.py`
- Goal:
  - identify prompt-frame asymmetries across companion generation families
  - separate true interface-content differences from broader framing-richness differences

## Bottom Line

Current companion comparisons are **not** clean single-variable ablations of control representation.
They are better understood as **deploy-route / prompt-family comparisons**.

The main asymmetry is not in `execution_interface.py` itself. That file is fairly clean:
- it maps signals into interface labels in a mostly symmetric way
- phase overrides are deterministic and shared
- renderers expose different interface families, but the ontology construction itself is systematic

The stronger asymmetry comes from `actor_prompt.py`:
- different route families receive materially different identity framing
- different levels of boundary / restraint emphasis
- different strengths of continuity / anti-drift instruction
- different explanations of how strictly control should override default helpfulness
- different amounts of prose meta-guidance about what not to do

So if one route looks more coherent or less jumpy, that result currently mixes:
- control representation quality
- interface executability
- prompt richness / framing richness
- obedience salience

## High-Level Finding by File

### `execution_interface.py`

Relatively symmetric / lower-risk:
- `build_execution_interface(...)`
- `build_execution_interface_from_rel(...)`
- `build_execution_interface_from_instruction_labels(...)`
- `_apply_phase_overrides(...)`

Why:
- all interface variants are built from the same bucketization logic
- phase overrides are shared across variants
- renderers differ in surface form, but the mapping logic is explicit and systematic

Remaining caveat:
- different interface families still expose different amounts of surface control detail:
  - discrete chart
  - continuous numeric interface
  - ordinal / banded / hybrid renderings
- this is a real deploy difference, but it is closer to the intended experimental variable

### `actor_prompt.py`

Main source of asymmetry:
- route builders are not prompt-frame matched
- routes differ not only in control content, but also in broader system-role framing

This means current route comparisons are family comparisons, not minimal representation swaps.

## Concrete Asymmetry Inventory

### 1. Identity Framing Is Not Matched

The top-level persona / role assignment differs across builders.

Examples:
- `build_actor_system_prompt(...)`
  - frames the model as `"忠诚型陪伴 AI" 的表达层（Actor）`
  - adds `"忠诚的机器人管家"` identity
  - explicitly says the model must lower posture and emotionally support / give executable help
- prose baselines
  - mostly frame the model as `长期陪伴型 AI`
- role-play baseline
  - explicitly frames the model as a `温暖、熟悉...的老朋友`
- several explicit-state builders
  - frame the model as `长期陪伴型对话系统的表达层`

Impact:
- identity framing alone can shift warmth, subordination, helpfulness pressure, and “human-like continuity”
- this is not just interface content

Risk level: high

### 2. Boundary / Restraint Intensity Is Not Matched

Different builders place different amounts of anti-overreach instruction into the system prompt.

Examples:
- `build_actor_system_prompt(...)`
  - has a long anti-toolness / anti-coaching / disclosure-governance block
  - includes explicit disclosure safety grammar
- `build_relational_instruction_baseline_system_prompt(..., stronger=True)`
  - gets a very strong extra steady-state block
- `build_prompt_only_baseline_system_prompt(..., style_strength='generic')`
  - gets a much thinner frame
- execution-route builders
  - often add explicit “do not self-expand / do not self-upgrade relation / obey constraints over default helpfulness”

Impact:
- some routes are more protected against overexpansion before interface content even starts doing work

Risk level: high

### 3. Continuity / Anti-Drift Language Is Stronger in Some Builders Than Others

Continuity requirements are not uniformly matched.

Examples:
- stronger prose baseline:
  - explicit steady-state instructions
  - `姿态变化要渐进`
  - `不要为了显得更懂而临时升温、降温或改口`
- bridge / explicit-state builders:
  - repeated warnings against sudden warming, overshoot, compensatory care
- execution-route builders:
  - explicit bans on deriving new constraints or upgrading relation from summary alone
- generic baseline:
  - only minimal stability wording

Impact:
- if one route is more stable, part of that may come from stronger continuity wording rather than control representation alone

Risk level: high

### 4. Execution Override Salience Is Not Matched

Some routes explicitly tell the model that control info overrides its default assistant prior.

Strong examples:
- `build_explicit_rel_state_projected_execution_system_prompt(...)`
  - says relation and expression constraints are separate
  - says constraints override default helpfulness
  - says not to infer new constraints from relation summary
  - repeatedly bans exposing or paraphrasing control info
- `build_explicit_rel_state_projected_continuous_execution_system_prompt(...)`
  - says continuous signals are expression constraints
  - warns against overshooting from slight increases
- `build_explicit_rel_state_projected_soft_execution_system_prompt(...)`
  - similarly frames the chart as execution constraints

Weaker in prose-only families:
- prose baselines mostly say “follow this stance naturally”
- they do not usually give the same hard override framing against default helpfulness

Impact:
- a route may win because its control is more salient and binding, not only because its interface ontology is better

Risk level: very high

### 5. Failure-Mode Preemption Is Not Symmetric

Certain builders explicitly preempt common failure modes.

Examples:
- `build_actor_system_prompt(...)`
  - anti-list
  - anti-menu
  - anti-coaching
  - only one gentle follow-up
- stronger prose baseline
  - anti-toolness
  - anti-template
  - anti-relationship-overread
- execution-route builders
  - anti-compensatory warmth
  - anti-extra follow-up
  - anti-meta-talk
  - anti-self-derived upgrade

Impact:
- measured gains partly reflect richer preventive prompt engineering at the route level

Risk level: high

### 6. Memory Exposure Is Similar but Not Perfectly Matched

Many builders include memory previews, but not always with the same cap or same framing:
- some use `[:2]`
- some use `[:3]`
- some use explicit preference / boundary / recent-summary blocks
- some just use generic preview snippets

Impact:
- lower than identity / override asymmetry
- still contributes to route richness differences

Risk level: medium

### 7. Role-Play Baseline Is Intentionally a Different Prompt Family

`build_roleplay_relational_baseline_system_prompt(...)` is not just “same route without interface”.
It injects:
- old-friend framing
- warmth / familiarity emphasis
- anti-overplay guidance

Interpretation:
- useful as a reviewer-facing alternative explanation baseline
- not suitable as a clean ablation anchor

### 8. Generic Baseline Is Also Intentionally a Different Family

`build_prompt_only_baseline_system_prompt(..., style_strength='generic')` is intentionally much thinner.

Interpretation:
- useful for showing the result does not depend on contrasting only against a paper-specific baseline
- not useful for isolating the effect of control representation

### 9. Continuous vs Discrete Interface Comparison Is Cleaner Than Prose vs Execution Family Comparison

Inside `execution_interface.py`, the contrast among:
- continuous
- ordinal soft
- banded
- hybrid
- discrete chart

is methodologically cleaner than the broader actor-prompt family comparisons, because:
- they share more of the execution-route framing logic
- the main variable is closer to interface surface / ontology

Interpretation:
- interface-family screening is more believable as an interface-form study
- prose-vs-execution comparisons are more clearly route-family studies

## Practical Interpretation

The current companion setup most defensibly supports:
- which deploy route family is more executable in practice
- which interface family is more stable under the current downstream model

It does **not** cleanly support:
- a strict claim that only the minimal interface representation changed
- a strict claim that all gains come from chart semantics rather than broader prompt framing

## What To Fix for the Rerun

For a symmetry-focused mini-rerun, the following prompt blocks should be matched across routes:

1. Shared identity block
- same top-level role
- same personality baseline
- no route-specific `loyal robot steward` vs `old friend` vs `expression layer` drift

2. Shared safety / anti-manipulation block
- same wording across routes

3. Shared anti-toolness / anti-overexpansion block
- same wording across routes

4. Shared continuity / steady-state block
- same wording across routes

5. Shared memory block
- same number of memory items
- same formatting

6. Shared output requirements
- same directness, list-avoidance, follow-up cap, task-priority wording

Only these should vary:
- route-specific relational summary source
- route-specific execution interface text
- route-specific state-derived vs label-derived control content

## Recommended Reading of Existing Results

Until a symmetry rerun is done, current companion results should be read as:
- realistic deploy-family comparisons
- not perfectly prompt-matched single-variable ablations

That does not invalidate the results.
It just narrows the cleanest claim:
- from `this specific minimal interface variable alone caused the gain`
- to `this route family / deploy interface family is more executable under current implementations`
