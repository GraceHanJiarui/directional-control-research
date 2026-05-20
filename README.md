# Directional Control Research

This directory tracks the directional-control / boundary-suppressibility mechanism line.

## Canonical Sources

Use these files as the authoritative record for the current mechanism work:
- `directional_control_research/mechanism_experiment/README.md`
- `directional_control_research/mechanism_experiment/docs/experiment_design.md`
- `directional_control_research/mechanism_experiment/docs/failed_runs_log.md`

## Current Best-Supported Claims

- Under explicit user-side boundary instructions, `anti_underanswer` is harder to suppress than `baseline`, while `minimal_boundary` is easier to suppress.
- Under comparable assistant framing, the untouched base model is less bounded and more continuation-prone than the SFT variants.
- Different post-training families have different suppressibility profiles; not all trained biases are equally sticky.
- Later assistant-token supervision carries both continuation pressure and stopping regularization. True EOS helps, but EOS alone is not enough; a continuous tail span helps more.
- The current uncertainty probe does not support a simple uncertainty-compensation explanation as the main cause of long-answer persistence.
- Compression-vs-pruning results suggest that `anti_underanswer` is more strongly tied to content budgeting / pruning difficulty than to mere wording compression difficulty.
- New mechanism probes suggest that anti-underanswer persistence is not a single failure mode: it reflects both earlier planning / content-budgeting effects and later continuation / stopping effects.

## Current Mechanism Map

The working picture is:
1. Base models show a raw continuation tendency under assistant framing.
2. Post-training regularizes that tendency into assistant behavior.
3. Different training families reshape the regularized policy in different directions.
4. Boundary failures appear to include both early planning overshoot and late stopping failure.
5. New branchpoint / controllability / forced-prefix probes suggest that anti-underanswer stickiness is not mainly a one-step local continue preference; it appears to be a mixed directional-control problem that persists both before and after a minimally sufficient answer point is reached.
6. In the current hypothesis map, H2 (planning / content budgeting) and H3 (assistant-policy prior / post-training reshaping) are the strongest explanations; H1 (stopping structure) is clearly relevant but not sufficient alone; H4 is partially supported; H5 is currently not positively supported by the uncertainty probe.

## Cleanup Note

Earlier console-based edits damaged several non-canonical files. Those files have either been repaired, regenerated from clean sources, or deleted if they were abandoned probes.

## Audit Note

A focused code audit was run over the experiments that currently support the main claims.

Current status:
- No newly found code issue appears to invalidate the retained core conclusions.
- The retained conclusions remain valid only under the current narrowed wording; they should not be overstated into stronger causal claims than the code actually supports.

Important boundaries:
- Invalid or unstable lines remain excluded from evidence:
  - `clarify_first_sft_v1`
  - old `branchpoint_probe_v1`
  - `compression_only_sft_v1` / `pruning_only_sft_v1`
  - `compression_only_proxy_v2` / `pruning_only_proxy_v2`
  - `baseline_then_minimal_stage2_v1`
  - `baseline_then_preference_*_stage3_v1`
- `logit_branchpoint_probe_v1` compares whole suffix candidates by average logprob; it is not a pure single-token EOS test.
- Generation post-processing still uses explicit role-marker truncation and a small amount of historical tail cleanup, so exact character counts should not be treated as the sole source of truth.
- The current preference-stage result now includes a larger stable GPU medium run: it supports a medium-strength amplification reading, but still does not yet justify a full preference-stage causal claim.

## Practical Rule

If there is any conflict between this top-level summary and a detailed note elsewhere, follow the mechanism-experiment documents listed under `Canonical Sources`.

## Preference-Stage Update

The preference-stage line now has two usable stable runs on top of `baseline_sft_v5`:
- `baseline_then_preference_expand_stage3_gpu_medium_v1`
- `baseline_then_preference_expand_stage3_gpu_large_stable_v1`

What now appears stable across both runs:
- later preference-like optimization does push the system in the same broad expansionary direction as the anti-oriented stage;
- this shows up most clearly in forced-prefix continuation and in non-flat asymmetric controllability.

What the comparison now clarifies:
- `gpu_medium_v1` remains the strongest current preference-stage result (`mean continuation chars = 28`);
- `gpu_large_stable_v1` is still supportive (`mean continuation chars = 19.42`), but it does not exceed the medium run;
- so the preference-stage effect now looks real but non-monotonic, rather than something that simply grows with more data or a larger stable setting.

The current stage-split picture is therefore:
- baseline SFT already defines the assistant-policy space;
- later anti-oriented SFT can strongly amplify the asymmetry;
- later preference-like optimization can also amplify it, but the strongest current preference evidence remains medium-strength and still falls below `baseline_then_anti_stage2_v1`.

Cross-over reversal update:
- a cleaner `v2` rebuild now exists after fixing three confounds:
  - non-baseline preference pairs now use policy-consistent system anchors;
  - broken / over-jumping minimal-side pair constructions were filtered or dropped;
  - DPO training no longer depends on the unstable Windows JSON `datasets` loader.
- under this cleaner setup we now have:
  - one strong retained reversal result:
    - `anti_underanswer_sft_v5 -> preference_minimal`
  - one weaker but now interpretable midpoint-pullback result:
    - `minimal_boundary_sft_v5 -> preference_baseline_task_primary_minanchor`
  - no retained outward-from-minimal reversal result.

What now appears supported:
- later preference-like optimization is not limited to same-direction amplification;
- in at least one important direction, it can meaningfully pull back an already sticky anti-oriented SFT policy.

What the strongest retained result now looks like:
- `anti_then_preference_minimal_stage3_gpu_large_stable_v2` becomes very short again under the main suppressive Phase 2 modes:
  - `neutral = 12.0`
  - `avoid_underanswer = 14.25`
  - `scope_minimal_sufficient = 13.0`
  - `do_not_add_unasked_help = 15.25`
- on forced-prefix continuation it stops immediately on `9/12` probe items, with `mean continuation chars = 1.0`;
- its asymmetric controllability profile becomes much flatter and more minimal than direct anti-underanswer.

What the cleaner opposite-side result now shows:
- `minimal_then_preference_baseline_task_primary_minanchor_stage3_gpu_medium_v2` is no longer a dirty drift run;
- it yields a partial midpoint pullback:
  - `neutral = 14.58`
  - `avoid_underanswer = 34.58`
  - `scope_minimal_sufficient = 21.67`
  - `do_not_add_unasked_help = 27.25`
  - forced-prefix: `7/12` immediate stops, `mean continuation chars = 8.42`
- but it is still clearly weaker and less clean than the anti-side pullback.

What was dropped after the cleaner rebuild:
- old `minimal -> one_layer` evidence should not be used;
- once sentence-splitting was fixed, that pair construction no longer yielded valid samples;
- earlier dirty `minimal -> preference_expand` style runs should be treated as diagnosis, not retained evidence.

So the stage-split picture is now:
- same-direction amplification remains the strongest overall evidence;
- but we now also have one strong later-stage reversal result (`anti -> preference_minimal`);
- and one weaker partial midpoint pullback on the minimal side;
- reversal capacity therefore appears real but strongly asymmetric across policy sides.

## Bundled Generalization Update

A repaired eval-only bundled-generalization matrix is now also usable as evidence.
On four bundled axes (`scope`, `interaction`, `help`, `caution`), the stable models do not behave like a single clean one-dimensional control problem.
Instead:
- `baseline` stays relatively flat and stable;
- `minimal` tends to follow the requested bundled direction in a mild, symmetric way;
- `anti_underanswer` shows a more imbalanced response structure across bundled directions;
- `baseline_then_anti_stage2_v1` shows an even stronger bundled-control imbalance.

This strengthens the current bundled-policy reading: the hard-to-suppress phenomenon is not just "more words". It generalizes to nearby high-level assistant-policy controls as a broader control-imbalance pattern.

## Second-Family Replication Update

A second-family replication line is now also usable on an open English chat model:
- `HuggingFaceTB/SmolLM2-1.7B-Instruct`

Current result:
- the model family is different from Qwen;
- the language is English rather than Chinese;
- but the key directional pattern still replicates in narrowed form.

What currently replicates:
- `anti_underanswer` remains harder to suppress than `baseline` under the main Phase 2 boundary modes;
- `anti_underanswer` also continues more strongly than `baseline` under forced-prefix continuation;
- the family still shows asymmetric bundled-control behavior rather than a single clean one-axis control pattern.

Boundary:
- this is a cross-family and cross-language replication, not a same-language same-task numerical reproduction;
- the SmolLM2 family is more verbose overall than the Qwen line, so the strongest claim is directional replication rather than direct metric equality.

## Bundled-Policy Update

The current mechanism picture should now be read in a more bundled way.

The hard-to-suppress over-expansion effect does not look like a single shallow feature such as a local continue token habit, a single clarify-first switch, or a single next-step template.
Instead, the current evidence points to a bundled assistant-policy bias that jointly affects:
- content budgeting,
- when to add one more step,
- when to clarify,
- when to keep explaining,
- and when to stop.

This is why cross-direction generalization is hard to isolate into a perfectly single-axis training family:
- high-level assistant-policy directions are not naturally clean, local, or independent;
- once trained, they tend to move multiple bundled behaviors together.

Important future-work boundary:
- beyond `emoji_only`, we still lack a second clean high-level SFT direction that survives full evaluation;
- so the retained evidence does not yet show whether hard suppressibility is specific to over-expansion or is a broader property of high-level SFT-stabilized assistant-policy biases.

Additional negative exploration update:
- two additional high-level direction attempts were now run and should be treated as negative exploration, not retained evidence:
  - `affect_attuned vs affect_flat`
  - `deferential_uncertain vs decisive_direct`
- both lines were rebuilt with cleaner data and GPU stage-2 training, and both passed smoke-level training stability;
- neither produced a clean retained high-level policy axis under fuller evaluation;
- this should currently be read as:
  - we did try additional high-level directions seriously,
  - but within the present compact 12/18-case stage-2 framework they did not yield evidence comparable to `anti_underanswer`.

Current interpretation update:
- this does not show that over-expansion is the only possible sticky high-level direction;
- it does support a narrower comparative claim:
  - within the present framework, `anti_underanswer / over-expansion` behaves like a comparatively privileged direction rather than a generic example of arbitrary high-level SFT bias.

## Next Experiments

The highest-yield next experiments are now:

1. Deepen the reversal line around the retained `anti -> preference_minimal` result.
Most useful follow-ups:
- per-case paired deltas against direct `anti_underanswer_sft_v5`;
- a bundled-generalization eval on the retained reversal line;
- light resampling / confidence-interval reporting rather than many more training variants.

2. Decide whether one more clean high-level SFT direction is worth the time.
Why:
- this is still the main remaining generality gap, but two recent negative explorations (`affect`, `stance`) lowered the expected value of continuing to brute-force new axes in the current framework.

4. Add at least one more clean high-level SFT direction beyond `anti_underanswer`.
Why:
- without that contrast, the project still cannot cleanly answer whether sticky suppressibility is relatively unique to over-expansion or reflects a broader class of high-level SFT-stabilized assistant-policy biases.
