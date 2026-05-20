# Mechanism Experiment

This directory contains the active mechanism experiments for the directional-control line.

## Current Hypothesis Status

### H1: EOS / stopping mechanism
Status: **supported, but not sufficient on its own**.

What supports it:
- `anti_prefix50` becomes extremely long;
- `anti_prefix50_plus_true_eos_v2` pulls that back noticeably;
- `anti_prefix50_plus_tailspan_v3` pulls it back further.

What this means:
- stopping cues matter;
- true EOS supervision helps;
- but EOS alone is not enough;
- a continuous tail span matters as well.

So H1 is supported in a narrowed form:
- stopping is part of the story,
- but it is not only a single-token EOS problem.

### H2: high-level planning / discourse policy
Status: **strongly supported**.

What supports it:
- planning-vs-stopping reading shows clear early overshoot cases;
- compression-vs-pruning shows that anti-underanswer often fails at content budgeting rather than mere wording compression;
- branchpoint probing does not point to a simple one-step continue preference as the main explanation.

What this means:
- the model often chooses the wrong discourse path early,
- not just the wrong stopping point late.

### H3: alignment prior / assistant-policy prior
Status: **strongly supported**.

What supports it:
- `base` under comparable assistant framing is much less bounded and more continuation-prone;
- SFT regularizes that raw tendency;
- different SFT families then reshape suppressibility in different directions;
- a later anti-oriented SFT stage can amplify the asymmetry further.

What this means:
- post-training is not creating the whole tendency from nothing;
- it is regularizing and reshaping a pre-existing continuation tendency into more assistant-like policies.

### H4: supervision sparsity / branch-point sparsity
Status: **partially supported**.

What supports it:
- `emoji_only` transfers very differently from anti-underanswer;
- short / narrow control looks much harder than shallow surface-style transfer;
- loss-level probes show that structurally important supervision is spread across later answer spans, not a few local tokens.

What this means:
- short-style control is not behaving like dense local style transfer;
- it looks more like a sparse, path-dependent policy problem.

### H5: uncertainty-compensation
Status: **not positively supported in the current simple form**.

What we tested:
- token-level entropy and margin proxies on the dedicated uncertainty probe.

What we found:
- longer outputs are generally not associated with higher entropy in the simple way this hypothesis predicts;
- anti-underanswer often looks longer while remaining relatively confident.

So the current update is:
- H5 is weakened rather than strengthened;
- if uncertainty still matters, it likely interacts with other mechanisms rather than acting as the main simple driver.

## What Still Looks Worth Doing Beyond H1-H5

Even after H1-H5, there are still a few mechanism directions worth pursuing.

### 1. Quantitative planning-vs-stopping annotation
This is now completed for the focused `v2` pack.

Current summary:
- `80` rows labeled, `0` unlabeled
- overall:
  - `none = 33` (`41.25%`)
  - `planning = 8` (`10.0%`)
  - `stopping = 19` (`23.75%`)
  - `mixed = 8` (`10.0%`)
  - `unclear = 12` (`15.0%`)
- overall means:
  - `planning_overshoot = 0.338`
  - `stopping_failure = 0.662`

Most important decomposition:
- under `scope_minimal_sufficient`, planning failures are more common than stopping failures:
  - `planning = 17.5%`
  - `stopping = 12.5%`
- under `do_not_add_unasked_help`, stopping failures dominate:
  - `stopping = 35.0%`
  - `planning = 2.5%`

By model:
- `baseline` is the cleanest retained line:
  - `none = 62.5%`
  - `planning_overshoot mean = 0.125`
  - `stopping_failure mean = 0.375`
- `anti` is more stopping-heavy than baseline:
  - `stopping = 31.25%`
  - `stopping_failure mean = 0.875`
- `baseline_then_anti_stage2` is the most pathological:
  - `planning = 31.25%`
  - `stopping = 31.25%`
  - `mixed = 25.0%`
  - `planning_overshoot mean = 0.812`
  - `stopping_failure mean = 1.062`

What this adds:
- the anti-underanswer gap is now quantitatively supported as mixed rather than only qualitatively read;
- planning matters more under tighter-scope instructions;
- stopping dominates more under explicit “do not add help” instructions.

### 2. Same-information compression vs true pruning
This would distinguish:
- concise rephrasing of the same content;
- real content budgeting that removes secondary explanation, examples, or caveats.

Why it matters:
- it would sharpen the planning-vs-stopping distinction;
- it would also test whether short-style difficulty is mostly a compression problem or a content-selection problem.

### 3. Preference-stage extension
A cleaner SFT-vs-preference comparison tests whether stickiness is already largely present at SFT or whether later preference optimization can either sharpen or reverse it.

Current cross-over reversal status:
- retained:
  - `anti_underanswer_sft_v5 -> preference_minimal`
- not retained:
  - `minimal_boundary_sft_v5 -> preference_expand`

Why this matters:
- the retained anti-to-minimal run shows that later preference-like optimization can meaningfully pull back an already-shaped sticky anti policy;
- the failed opposite-direction run means we still do not have symmetric reversal evidence.

### 5. High-level direction contrast beyond anti-underanswer
We still need at least one additional clean high-level SFT direction beyond `anti_underanswer` and the shallow `emoji_only` contrast.
The key target is a direction that is:
- not just a surface style;
- stable under smoke and fuller evaluation;
- and comparable under the same suppressibility probes.

Why it matters:
- it would let us test whether hard suppressibility is relatively unique to over-expansion, or whether a broader class of high-level SFT-stabilized assistant-policy biases becomes similarly sticky.

### 6. Broader model-family replication
A second compact family beyond the current Qwen line would test how much of the current mechanism picture generalizes.

Why it matters:
- it would strengthen the external validity of the mechanism account without requiring a full large-scale replication.

## Mechanism Update: Compression vs Pruning

A new evaluation-only probe now distinguishes between two different notions of "being shorter":
- `same_information_compression`: preserve the content but compress the phrasing
- `true_pruning`: remove secondary explanation and keep only the core answer plus the first key point

Current result:
- `baseline` behaves sensibly under both controls and gets slightly shorter
- `anti_underanswer` reacts badly to `same_information_compression`, often becoming much longer instead of shorter
- `true_pruning` pulls `anti_underanswer` back somewhat, but not nearly to baseline

Current interpretation:
- the anti-underanswer gap is not best described as a pure wording-compression failure
- it is better described as a content-budgeting / pruning failure
- this strengthens H2 and H4 more than H5

This also helps sharpen the planning-vs-stopping split:
- some cases reflect early overshoot in how much content the model decides to include
- others still reflect late stopping failure after the core point has already been delivered

## Stage-Split Update: Preference Expand Runs

The preference-stage line now has two usable stable runs.

Setup:
- stage 1: `baseline_sft_v5`
- stage 3-like preference update: `anti_underanswer_response > baseline_response`
- current usable runs:
  - `baseline_then_preference_expand_stage3_gpu_medium_v1`
  - `baseline_then_preference_expand_stage3_gpu_large_stable_v1`

What the usable runs show:
- both runs push behavior away from baseline in the same broad expansionary direction;
- both runs increase continuation after a minimally sufficient prefix;
- both runs produce non-flat asymmetric controllability rather than staying approximately baseline-like.

What the comparison adds:
- `gpu_medium_v1` remains the strongest current preference-stage result (`mean continuation chars = 28`);
- `gpu_large_stable_v1` remains supportive but weaker (`mean continuation chars = 19.42`);
- so the preference-stage effect now looks real but non-monotonic under stable settings, rather than simply increasing with more data or a larger run.

So the current stage-split update is:
- later preference-like optimization does appear to push the system in the same expansionary direction;
- the strongest current amplification still comes from the anti-oriented SFT stage;
- preference-like stage evidence is now clearly above smoke-level, but it still should not be overread as a full causal decomposition or as a monotonic scaling result.

Cross-over reversal update:
- a cleaner `v2` rebuild was run after fixing preference-pair anchor inconsistency, broken minimal-side pair constructions, and the unstable Windows JSON DPO loader;
- `anti_then_preference_minimal_stage3_gpu_large_stable_v2` is now the primary retained reversal result;
- `minimal_then_preference_baseline_task_primary_minanchor_stage3_gpu_medium_v2` is now a weaker but interpretable partial midpoint-pullback result;
- `minimal_then_preference_expand*` and old `one_layer` evidence are not retained.

What the retained anti-to-minimal reversal now shows:
- Phase 2 average lengths collapse further to:
  - `neutral = 12.0`
  - `avoid_underanswer = 14.25`
  - `scope_minimal_sufficient = 13.0`
  - `do_not_add_unasked_help = 15.25`
- forced-prefix continuation becomes:
  - `stop_immediate = 9`
  - `continue_statement = 3`
  - `mean continuation chars = 1.0`
- asymmetric controllability becomes much flatter across `scope`, `interaction`, and `help`.

Interpretation:
- later preference-like optimization can, in at least one direction, genuinely pull back an already sticky anti-oriented SFT policy;
- this strengthens the stage account beyond same-direction amplification alone.

What the cleaner minimal-side midpoint line shows:
- `minimal_then_preference_baseline_task_primary_minanchor_stage3_gpu_medium_v2` no longer drifts into a dirty high-expansion regime;
- but it remains clearly weaker than the anti-side pullback:
  - Phase 2 means:
    - `neutral = 14.58`
    - `avoid_underanswer = 34.58`
    - `scope_minimal_sufficient = 21.67`
    - `do_not_add_unasked_help = 27.25`
  - forced-prefix:
    - `stop_immediate = 7`
    - `continue_statement = 4`
    - `continue_question = 1`
    - `mean continuation chars = 8.42`

Boundary:
- the cleaner minimal-side result is a partial midpoint pullback, not a symmetric clean reversal;
- the opposite outward-from-minimal reversal still did not produce a retained line;
- so the current evidence supports asymmetric reversal capacity, not a fully symmetric late-stage rewrite story.

## Stage-Split Update: Baseline Then Anti Stage 2

A new SFT-internal stage split now shows that the asymmetry can be amplified inside SFT itself.

Setup:
- stage 1: `baseline_sft_v5`
- stage 2: continue training from the baseline adapter on anti-underanswer data

Current usable result:
- `baseline_then_anti_stage2_v1`

What it shows:
- Phase 2 average lengths move far above baseline even under suppressive modes;
- forced-prefix continuation becomes much stronger than direct `baseline_sft_v5`;
- the model continues in every forced-prefix probe item in the current run.

Interpretation:
- a second anti-oriented SFT stage is already sufficient to further push a baseline assistant policy toward hard-to-suppress over-expansion;
- this means the asymmetry is not limited to a single one-shot direct SFT family;
- at least part of the effect can be sharpened by later directional fine-tuning inside SFT itself.

Boundary:
- the parallel `baseline_then_minimal_stage2_v1` run was unstable and is not currently usable as evidence.

## Audit Update: Code Validity Review

A focused review was run over the scripts that support the currently retained claims:
- `eval_lora_adapter.py`
- `eval_lora_adapter_phase2.py`
- `train_qlora_mechanism.py`
- `eval_logit_branchpoint_probe.py`
- `eval_asymmetric_controllability_matrix.py`
- `summarize_asymmetric_controllability_matrix.py`
- `eval_forced_prefix_continuation.py`
- `eval_uncertainty_probe.py`
- `eval_compression_vs_pruning_probe.py`

Current conclusion:
- no newly found bug appears to invalidate the retained core claims;
- the retained claims are still valid only in their narrowed form.

What remains excluded:
- `clarify_first_sft_v1`
- old `branchpoint_probe_v1`
- `compression_only_sft_v1` / `pruning_only_sft_v1`
- `compression_only_proxy_v2` / `pruning_only_proxy_v2`
- `baseline_then_minimal_stage2_v1`
- `baseline_then_preference_*_stage3_v1`

Important remaining boundaries:
- `logit_branchpoint_probe_v1` is a suffix-level logprob comparison, not a pure next-token EOS probe.
- The uncertainty script still has a `sentence_count_proxy` bug, but the existing H5 conclusion does not rely on that field.
- Post-processing cleanup in the eval scripts introduces a mild measurement risk for exact character counts, so length numbers should continue to be interpreted together with qualitative samples and the mechanism probes.

## Second-Family / Cross-Language Replication Update

A new second-family replication line is now usable on:
- `HuggingFaceTB/SmolLM2-1.7B-Instruct`

This line is not same-language with the Chinese Qwen main line, but it is the first compact external replication that currently runs cleanly enough to interpret.

### Smoke status
The three SFT variants are currently usable:
- `smollm2_1p7b_baseline_sft_en_v1`
- `smollm2_1p7b_anti_underanswer_sft_en_v1`
- `smollm2_1p7b_minimal_boundary_sft_en_v1`

They do not show the earlier failure patterns seen in TinyLlama / InternLM / the earlier small English Qwen runs:
- no role leakage;
- no template spill;
- no empty-output collapse;
- no obvious garbage-token degeneration.

### Phase 2 update
The key directional pattern replicates in narrowed form.
Average lengths under the four boundary modes show:
- `baseline` remains the least expansionary of the three;
- `anti_underanswer` remains the most expansionary under suppressive modes;
- `minimal_boundary` lands between them rather than fully collapsing to a tiny-response regime.

So the main anti-vs-baseline suppressibility gap does not appear to be unique to Qwen Chinese.

### Forced-prefix update
The forced-prefix probe is especially informative.
Current continuation means are:
- `baseline`: `80.25`
- `anti_underanswer`: `133.0`
- `minimal_boundary`: `97.58`

So even after the model is forced onto a minimally sufficient prefix, the anti variant continues more strongly than baseline in this second-family line as well.

### Asymmetric controllability update
The bundled controllability structure also remains nontrivial rather than collapsing into a single monotonic length effect.
The family is overall more verbose than Qwen, but the anti variant still shows a distinct bundled-control profile rather than simply matching baseline.

### Interpretation boundary
This should be read as:
- a cross-family, cross-language directional replication;
- not a one-to-one same-language numerical reproduction of the Qwen results.

The strongest supported claim is therefore:
- the core anti-underanswer asymmetry generalizes beyond the Qwen Chinese line in direction, even though the absolute family style differs.

## Bundled Assistant-Policy Update

The current interpretation should now be narrowed in a more explicit way.

### Main update

Over-expansion persistence is better treated as a bundled assistant-policy bias than as a single isolated behavior.

That bundle appears to include at least:
- a tendency to allocate too much content budget,
- a tendency to add one more step or one more layer of help,
- a tendency to keep the interaction moving forward,
- and a tendency to continue after a minimally sufficient answer point.

### Why this matters

This explains two things at once:
- why `anti_underanswer` is much harder to suppress than shallow styles like `emoji_only`;
- why cross-direction proxy families such as `next_step_heavy` are hard to keep cleanly single-factor.

The failure of a clean single-axis cross-direction family should therefore not be overread as evidence against the main mechanism story.
It is also evidence that these higher-level assistant-policy directions are not naturally disentangled.

### Current cross-direction status

`next_step_heavy_proxy_v1` is currently **not usable as evidence**.
Its smoke output was acceptable, but the fuller evaluations showed strong instability and multi-turn drift, so it should not be used for mechanism claims.

A repaired **eval-only bundled generalization** matrix is now usable.
Across the bundled axes `scope`, `interaction`, `help`, and `caution`:
- `baseline` stays comparatively flat and stable;
- `minimal` tends to follow the requested bundled direction in a mild and relatively symmetric way;
- `anti_underanswer` shows a more imbalanced bundled-control response;
- `baseline_then_anti_stage2_v1` shows an even stronger bundled-control imbalance.

So the current cross-direction update is:
- cross-direction generalization does appear to exist at the bundled-policy level;
- it should still not be framed as a clean single-axis mechanism;
- the more defensible claim is that sticky assistant-policy bias generalizes as broader control imbalance across nearby high-level directions.

### Additional high-level direction attempts

Two additional high-level SFT directions were tried as explicit contrastive directions beyond `anti_underanswer`:
- `affect_attuned vs affect_flat`
- `deferential_uncertain vs decisive_direct`

What was done:
- both lines were rebuilt as cleaner stage-2 experiments on top of `baseline_sft_v5`;
- the affect line went through multiple rebuilds (`v1`, same-content `v2`, emotional-case-only `v3`);
- the stance line was built as a same-core-content axis over `task_primary`, `clarify_next_step`, and `practical_troubleshooting`;
- all of these lines trained successfully and reached smoke-usable checkpoints.

What happened:
- none of them produced a retained clean high-level policy axis under fuller evaluation;
- `affect_attuned vs affect_flat` kept collapsing into a mixture of length change, comfort scripting, and broader interaction drift;
- `deferential_uncertain vs decisive_direct` was already prompt-steerable at baseline, but the stage-2 models did not consolidate the stance axis into a stable sticky direction, and the decisive line became noisy.

How to read this:
- these are negative explorations, not retained evidence;
- they do not show that the main line is wrong;
- they do show that additional high-level directions are harder to stabilize than the anti-underanswer line in the current compact stage-2 framework.

Comparative interpretation:
- the current evidence still does not justify saying that over-expansion is the only high-level direction that could ever become sticky;
- but it now does justify a narrower claim:
  - in the present mechanism framework, `anti_underanswer / over-expansion` appears comparatively privileged:
    - easier to stabilize,
    - easier to amplify,
    - and more likely to yield a clean suppressibility asymmetry than the other high-level directions we seriously tried.

## Best Next Mechanism Work

The next most informative experiments are now:

1. Stress-test the retained `anti -> preference_minimal` reversal line with evaluation, not many more training variants.
Best follow-ups:
- paired per-case deltas against direct `anti_underanswer_sft_v5`;
- bundled-generalization evaluation on the retained reversal line;
- simple resampling / confidence intervals for the retained comparisons.

2. Add one more clean high-level SFT direction beyond `anti_underanswer` only if time allows.
This is now the main remaining generality gap.
