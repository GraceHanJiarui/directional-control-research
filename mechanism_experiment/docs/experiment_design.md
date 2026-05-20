# Experiment Design

## H1-H5 Status

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
Status: **partially supported**.

What supports it:
- planning-vs-stopping reading shows clear early overshoot cases;
- some anti-underanswer failures happen before the model has even delivered the narrow first-step answer.

What this means:
- the model sometimes chooses the wrong discourse path early,
- not just the wrong stopping point late.

So H2 now has meaningful support, but not yet a fully quantified annotation result.

### H3: alignment prior / assistant-policy prior
Status: **partially supported to moderately supported**.

What supports it:
- `base` under comparable assistant framing is much less bounded and more continuation-prone;
- SFT regularizes that raw tendency;
- different SFT families then reshape suppressibility in different directions.

What this means:
- post-training is not creating the whole tendency from nothing;
- it is regularizing and reshaping a pre-existing continuation tendency into more assistant-like policies.

What is still missing:
- a cleaner preference-stage / RLHF-stage split.

So H3 is one of the strongest current hypotheses, but it is still not fully isolated by stage.

### H4: supervision sparsity / branch-point sparsity
Status: **partially supported**.

What supports it:
- `emoji_only` transfers very differently from anti-underanswer;
- `short/minimal` and anti-underanswer style changes are much harder to make stable than shallow surface styles;
- loss-level probes show that the later answer span carries structurally important supervision that cannot be reduced to a few local tokens.

What this means:
- short-style control is not behaving like dense local style transfer;
- it looks more like a sparse, path-dependent policy problem.

What is still missing:
- a same-information compression vs true-pruning split.

So H4 is plausible and increasingly supported, but still incomplete.

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
The focused `v2` annotation pack is now complete.

Current quantitative picture:
- `80` rows labeled, `0` unlabeled
- overall means:
  - `planning_overshoot = 0.338`
  - `stopping_failure = 0.662`
- overall label mix:
  - `none = 41.25%`
  - `planning = 10.0%`
  - `stopping = 23.75%`
  - `mixed = 10.0%`
  - `unclear = 15.0%`

Most important split:
- `scope_minimal_sufficient` shows more planning than stopping failure:
  - `planning = 17.5%`
  - `stopping = 12.5%`
- `do_not_add_unasked_help` is strongly stopping-dominated:
  - `stopping = 35.0%`
  - `planning = 2.5%`

This matters because it turns the earlier structured reading into a quantitative decomposition:
- the asymmetry is not just one thing;
- planning matters more when the user asks for a tighter scope;
- stopping matters more when the user explicitly forbids extra help.

### 2. Same-information compression vs true pruning
This would distinguish:
- concise rephrasing of the same content;
- real content budgeting that removes secondary explanation, examples, or caveats.

Why it matters:
- it would sharpen the planning-vs-stopping distinction;
- it would also test whether short-style difficulty is mostly a compression problem or a content-selection problem.

### 3. Preference-stage extension
A cleaner SFT-vs-preference comparison tests whether stickiness is already largely present at SFT or whether later preference optimization sharpens it further.

The original missing cross-over reversal controls have now been partially filled:
- retained:
  - `anti_underanswer_sft_v5 -> preference_minimal`
- partial / weaker:
  - `minimal_boundary_sft_v5 -> preference_baseline_task_primary_minanchor`
- not retained:
  - outward-from-minimal expansionary reversals

Why it matters:
- it tests whether later preference-like optimization can genuinely pull an already-shaped SFT policy back across the boundary, rather than only amplifying an aligned direction;
- it now supports a narrower but stronger claim:
  - reversal capacity exists,
  - but it is asymmetric across policy sides.

### 5. High-level direction contrast beyond anti-underanswer
We still need at least one additional clean high-level SFT direction beyond `anti_underanswer` and the shallow `emoji_only` contrast.
The key target is a direction that is:
- not just a surface style;
- stable under smoke and fuller evaluation;
- and comparable under the same suppressibility probes.

Why it matters:
- it would let us test whether hard suppressibility is relatively unique to over-expansion, or whether a broader class of high-level SFT-stabilized assistant-policy biases becomes similarly sticky.

Current negative exploration status:
- `affect_attuned vs affect_flat` was tried in multiple rebuilds, including a same-content version and an emotional-case-only version;
- `deferential_uncertain vs decisive_direct` was also tried as a same-core-content stance axis;
- both passed smoke-level training stability;
- neither yielded a retained clean high-level axis under fuller evaluation.

Interpretation boundary:
- this does not prove that no second high-level direction exists;
- it does show that additional high-level directions are substantially harder to stabilize than `anti_underanswer` in the current compact stage-2 setting.

Current comparative reading:
- the extra negative explorations strengthen a comparative claim, not an exclusivity claim;
- namely, `anti_underanswer / over-expansion` currently looks unusually stabilizable and unusually likely to yield clean suppressibility asymmetry, relative to the other high-level directions attempted so far.

### 6. Broader model-family replication
A second compact family beyond the current Qwen line would test how much of the current mechanism picture generalizes.

Why it matters:
- it would strengthen the external validity of the mechanism account without requiring a full large-scale replication.

## Update: Same-Information Compression vs True Pruning

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

Two stable preference-like runs are now available on top of `baseline_sft_v5`.

### Implemented split
- stage 1: `baseline_sft_v5`
- later preference-like update: `anti_underanswer_response > baseline_response`
- current usable runs:
  - `baseline_then_preference_expand_stage3_gpu_medium_v1`
  - `baseline_then_preference_expand_stage3_gpu_large_stable_v1`

### What the usable runs show
- both runs push behavior away from baseline in the same broad expansionary direction;
- both runs increase post-prefix continuation relative to baseline;
- both runs generate non-flat asymmetric controllability rather than leaving the system approximately baseline-like.

### What the run comparison adds
- `gpu_medium_v1` remains the strongest current preference-stage result (`mean continuation chars = 28`);
- `gpu_large_stable_v1` remains supportive but weaker (`mean continuation chars = 19.42`);
- so the current preference-stage picture is supportive but non-monotonic.

### Current interpretation
- preference-like optimization can continue to amplify the same broad asymmetry direction after baseline SFT;
- however, the strongest current amplification still comes from `baseline_then_anti_stage2_v1`;
- so the cleanest current reading is that both later SFT and later preference-like optimization can push in the same direction, but they are not yet shown to contribute equally, and the preference-stage scaling story is not simply monotonic.

### Cross-over reversal update
Cross-over reversal is no longer fully missing, and the line has now been rebuilt under cleaner `v2` conditions.

Important cleaner rebuild fixes:
- policy-consistent preference-pair anchors for non-baseline policies;
- hard filtering of over-jumping / bundled minimal-side targets;
- replacement of the unstable Windows `datasets` JSON loader in DPO training;
- removal of the old `one_layer` result after fixing its sentence-splitting bug.

Retained strong result:
- `anti_underanswer_sft_v5 -> preference_minimal` (`v2`)

Partial weaker result:
- `minimal_boundary_sft_v5 -> preference_baseline_task_primary_minanchor` (`v2`)

Non-retained opposite-direction attempts:
- `minimal_boundary_sft_v5 -> preference_expand`
- old `minimal -> one_layer`

Scaffolding that was added for these attempts:
- pair-generation script:
  - `scripts/generate_preference_pairs_cross_reversal_v1.py`
- generated pair files:
  - `data/built_pref_v1/preference_cross_expand_from_minimal_pairs_v1_train.jsonl`
  - `data/built_pref_v1/preference_cross_expand_from_minimal_pairs_v1_train_medium160.jsonl`
  - `data/built_pref_v1/preference_cross_minimal_from_anti_pairs_v1_train.jsonl`
  - `data/built_pref_v1/preference_cross_minimal_from_anti_pairs_v1_train_medium160.jsonl`
- medium-stable configs:
  - `configs/minimal_then_preference_expand_stage3_gpu_medium_v1_1p5b.yaml`
  - `configs/anti_then_preference_minimal_stage3_gpu_medium_v1_1p5b.yaml`
- logged wrappers:
  - `scripts/run_train_minimal_then_preference_expand_stage3_gpu_medium_v1_1p5b_logged.ps1`
  - `scripts/run_train_anti_then_preference_minimal_stage3_gpu_medium_v1_1p5b_logged.ps1`

What the retained anti-to-minimal reversal shows:
- later preference-like optimization is not limited to same-direction amplification;
- under the cleaner `v2` setup it still meaningfully pulls an already sticky anti SFT policy back toward a minimal regime.

Current retained metrics:
- Phase 2 means:
  - `neutral = 12.0`
  - `avoid_underanswer = 14.25`
  - `scope_minimal_sufficient = 13.0`
  - `do_not_add_unasked_help = 15.25`
- forced-prefix:
  - `9/12` immediate stops
  - `mean continuation chars = 1.0`

What the partial minimal-side midpoint result shows:
- a cleaner minimal-side pullback can be made interpretable;
- but it remains substantially weaker than the anti-side pullback.

Current partial metrics:
- Phase 2 means:
  - `neutral = 14.58`
  - `avoid_underanswer = 34.58`
  - `scope_minimal_sufficient = 21.67`
  - `do_not_add_unasked_help = 27.25`
- forced-prefix:
  - `7/12` immediate stops
  - `mean continuation chars = 8.42`

What the failed opposite-direction attempts mean:
- the old minimal-side outward lines were partly confounded by pair design and one broken sentence-splitting path;
- after cleaning those issues, the anti-side reversal remains strong while outward-from-minimal reversal still does not produce a retained line;
- so the remaining asymmetry is not just an artifact of the old training entry or anchor mismatch.

Current stage-split interpretation:
- same-direction amplification remains the stronger and cleaner overall evidence;
- but one strong reversal result now exists (`anti -> preference_minimal`);
- and one weaker partial midpoint pullback now exists on the minimal side;
- we still do not have symmetric clean reversal evidence in both directions.

### Best next experiments on this line

1. Stress-test `anti -> preference_minimal` with evaluation, not many more training branches:
- paired per-case comparison against direct anti;
- bundled-generalization eval on the reversal line;
- confidence intervals / resampling.
2. Add at least one more clean retained high-level SFT direction beyond `anti_underanswer` if remaining time permits.

## Stage-Split Update: SFT Internal Amplification

A new stage-split probe asks whether a later directional SFT update is already enough to amplify the asymmetry.

### Implemented split
- stage 1: `baseline_sft_v5`
- stage 2a: continue from baseline into `anti_underanswer`
- stage 2b: continue from baseline into minimal_boundary

### Current usable result
Only `baseline_then_anti_stage2_v1` is currently usable.
The `baseline_then_minimal_stage2_v1` run became unstable and should not be used for mechanism claims.

### What the usable run shows
- under Phase 2 boundary evaluation, `baseline_then_anti_stage2_v1` remains highly expanded;
- under forced-prefix continuation, it continues on every current probe item;
- under asymmetric controllability, it becomes more directionally unstable than baseline.

### Current interpretation
This strengthens the stage account in a narrower but more causal way:
- a baseline assistant policy is not the end of the story;
- a later anti-oriented SFT stage can further amplify hard-to-suppress over-expansion;
- therefore, the asymmetry can be strengthened within SFT itself, even before any separate preference/RLHF-like stage is introduced.

## Audit Update: Validity Boundaries

A focused audit was run over the experiment code currently supporting the retained claims.

### Audit result

No newly found code issue currently appears to invalidate the retained core conclusions, provided the claims remain narrowed.

### What remains valid

- Q1 / Q2 / Q3:
  - explicit user-side boundary evaluation still supports the main suppressibility and family-difference claims;
- Q4:
  - the loss-level prefix / true-EOS / tail-span line still supports the claim that later supervision carries both continuation pressure and stopping structure;
- mechanism probes:
  - `logit_branchpoint_probe_v1`
  - `asymmetric_controllability_matrix_v1`
  - `forced_prefix_continuation_v1`
  remain usable in their current interpreted form;
- stage split:
  - `baseline_then_anti_stage2_v1` remains usable.

### What remains excluded from evidence

- `clarify_first_sft_v1`
- old `branchpoint_probe_v1`
- `compression_only_sft_v1` / `pruning_only_sft_v1`
- `compression_only_proxy_v2` / `pruning_only_proxy_v2`
- `baseline_then_minimal_stage2_v1`
- `baseline_then_preference_*_stage3_v1`

### Remaining interpretation boundaries

- `logit_branchpoint_probe_v1` compares average logprob over whole candidate suffixes, not pure next-token EOS probability.
- `eval_uncertainty_probe.py` still contains a `sentence_count_proxy` bug; the current H5 conclusion does not depend on that field and therefore remains usable.
- Eval post-processing still trims explicit role-marker spillover and a small set of historical tail artifacts; exact character counts should therefore remain secondary to converging evidence across qualitative reads and mechanism probes.

## Second-Family / Cross-Language Replication

A usable compact replication line is now available on:
- `HuggingFaceTB/SmolLM2-1.7B-Instruct`

This line changes both language and family relative to the Chinese Qwen main line, so it should be interpreted as an external-validity extension rather than a pure same-language family control.

### What replicates
Under the English SmolLM2 line:
- `anti_underanswer` remains more expansionary than `baseline` under the main Phase 2 suppression modes;
- `anti_underanswer` also shows stronger continuation than `baseline` in forced-prefix continuation;
- the resulting control picture is still asymmetric and bundled rather than a simple one-axis length effect.

### What does not fully replicate
The absolute style is not the same as Qwen:
- SmolLM2 is more verbose overall;
- `minimal_boundary` remains cleaner than `anti_underanswer`, but not dramatically tiny;
- so the replication is directional rather than numerically identical.

### Current interpretation
This strengthens the external validity of the main mechanism account in a narrowed way:
- the anti-underanswer asymmetry is not only a Qwen-Chinese artifact;
- the same broad directional problem appears in another open chat family in English;
- and the forced-prefix continuation signal survives that cross-family, cross-language shift.

## Bundled Assistant-Policy Interpretation

The mechanism account should now be read with a stronger bundled-policy framing.

### Main idea

The current evidence does not point to a single shallow cause such as:
- a pure EOS problem,
- a pure next-token continue preference,
- a pure clarify-first toggle,
- or a pure extra-next-step toggle.

Instead, the evidence is more consistent with a bundled assistant-policy bias that jointly influences:
- planning / content budgeting,
- proactive help and next-step offering,
- clarify-versus-answer decisions,
- and later continuation / stopping persistence.

### Why the cross-direction line is hard

This bundled reading explains why cross-direction generalization is difficult to operationalize as a perfectly clean one-factor family.
High-level assistant-policy directions such as:
- over-next-step,
- over-clarify,
- over-helpfulness,
- over-structuring,
are not naturally local or independent.

When trained, they tend to co-move multiple policy dimensions at once.
So a failed attempt at a clean single-axis family should not automatically be read as a failed mechanism idea.
It can also mean that the target direction is itself inherently bundled.

### Current status of the first cross-direction attempt

`next_step_heavy_proxy_v1` is currently excluded from evidence.
Although its smoke output was usable, the fuller evaluations showed role leakage, multi-turn drift, and unstable expansion behavior.
So it should not be used for claims about generalization.

### Current best synthesis

The most defensible synthesis is now:
- over-expansion persistence is a bundled assistant-policy bias;
- `anti_underanswer` is one strong expression of that bundle;
- the bundle likely spans both early planning and later stopping behavior;
- and later post-training stages can amplify it further once a baseline assistant policy is already in place.
