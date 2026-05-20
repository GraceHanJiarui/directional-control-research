# Boundary-Suppressibility Asymmetry in Assistant Policies: A Mechanistic Study of Hard-to-Suppress Over-Expansion

## Abstract
Instruction-following assistants are often expected to respect explicit user boundaries such as "answer briefly," "do not elaborate too much," or "give only the minimal sufficient answer." In practice, some assistant policies are much harder to suppress than others: once a model has been trained away from under-answering, it may continue to elaborate even under direct boundary-setting prompts. This paper studies that directional asymmetry as a mechanism problem rather than a pure style-transfer problem. Using a controlled family of small post-training adapters on Qwen2.5-1.5B, we compare `baseline`, `anti_underanswer`, and `minimal_boundary` policies under matched evaluation settings. We then combine stage-split training, asymmetric controllability probes, forced-prefix continuation probes, compression-vs-pruning analysis, and cross-direction bundled-policy evaluation. The current evidence supports four main conclusions. First, anti-underanswer behavior is genuinely harder to suppress than baseline, while minimal-boundary behavior is easier to suppress. Second, the asymmetry is not well explained by a simple EOS failure or a simple uncertainty-compensation story. Third, the persistence appears to reflect a bundled assistant-policy bias spanning both early planning/content-budgeting and later continuation/stopping. Fourth, the same directional pattern survives both a later anti-oriented SFT stage and a cross-family, cross-language replication on SmolLM2-1.7B-Instruct. We argue that hard-to-suppress over-expansion should be understood as a post-training control-imbalance problem: once a baseline assistant policy is established, later training stages can further sharpen a sticky policy bundle that resists narrow user-side suppression.

## 1. Introduction
Modern assistant models are not judged only by correctness. They are also judged by boundary discipline: whether they answer the question asked, stop at the right point, and avoid adding unrequested structure, caveats, examples, or next steps. This matters for usability, controllability, and alignment. A model that systematically overshoots the user?s requested scope is often experienced as less obedient even when it is factually competent.

This paper studies a specific instance of that problem: the asymmetry between policies trained to avoid under-answering and policies trained to stay narrowly bounded. Empirically, these directions are not symmetric. A model pushed toward `anti_underanswer` becomes difficult to pull back with direct user instructions, whereas a model pushed toward `minimal_boundary` remains comparatively easy to control. The central question is not just whether this asymmetry exists, but what kind of mechanism it reflects.

The naive explanations are attractive but incomplete. One possibility is that the model simply fails to emit EOS. Another is that longer answers are driven by uncertainty compensation. A third is that the phenomenon is just a local style habit, like adding a certain phrase or emoji. The experiments in this project suggest a different picture. Hard-to-suppress over-expansion behaves more like a bundled assistant-policy bias: it affects not only how long the model talks, but how much content it budgets, whether it adds an extra layer of help, whether it keeps the interaction moving, and whether it continues even after a minimally sufficient answer point has already been reached.

### 1.1 Research question
We ask four linked questions:
1. Is `anti_underanswer` genuinely harder to suppress than comparable baseline and minimal-boundary policies under explicit user-side boundary instructions?
2. If so, is the effect mainly a stopping/EOS problem, an uncertainty problem, a local token-level continuation preference, or something higher-level?
3. At what stage of post-training does this asymmetry get amplified?
4. Does the directional pattern generalize beyond a single Chinese Qwen line?

### 1.2 Why this problem matters
This problem matters for at least three reasons.

First, it is practically important. Users often want a model to stay within a narrow scope: answer the question directly, give only the first step, avoid extra help, or stop after the core point. A model that cannot be cleanly suppressed in this way is less controllable even if it is otherwise aligned.

Second, it is scientifically useful. Many alignment failures are discussed as if they were single failure modes. This case gives a concrete setting in which a superficially simple behavior, ?talking too much,? decomposes into several mechanism candidates: planning, content budgeting, continuation pressure, stopping structure, and post-training priors.

Third, it is methodologically useful. The problem sits between standard prompt-following evaluation and full interpretability. It can be studied with careful small-scale adapters, matched probes, and stage-split training, making it a tractable testbed for mechanism-oriented post-training analysis.

## 2. Main contributions
This work makes five contributions.

1. It establishes a robust directional asymmetry: under explicit boundary-setting instructions, `anti_underanswer` is harder to suppress than `baseline`, while `minimal_boundary` is easier to suppress.
2. It shows that this asymmetry is not well captured by a simple EOS-only account, a simple uncertainty-compensation account, or a pure one-step local continue-preference account.
3. It proposes and supports a bundled assistant-policy interpretation in which over-expansion persistence spans both early planning/content-budgeting and late continuation/stopping.
4. It introduces stage-split evidence showing that the asymmetry can be further amplified both by a later anti-oriented SFT stage and, at medium strength, by a later preference-like stage.
5. It provides a compact external-validity extension: the core anti-vs-baseline directional pattern replicates in a second open chat family, SmolLM2-1.7B-Instruct, under English evaluation.

## 3. Experimental framing
### 3.1 Core policy families
The main Chinese line uses Qwen2.5-1.5B with three stable SFT variants:
- `baseline_sft_v5`
- `anti_underanswer_sft_v5`
- `minimal_boundary_sft_v5`

These variants are evaluated under matched user-side instructions that ask the model to stay narrow, avoid unasked help, or provide only the minimally sufficient answer.

### 3.2 Main evaluation axes
The project uses several complementary evaluations.

- Phase 2 boundary evaluation: tests behavior under explicit user boundary instructions such as `scope_minimal_sufficient` and `do_not_add_unasked_help`.
- Forced-prefix continuation: forces the model onto a minimally sufficient prefix and measures whether it immediately stops or keeps adding content.
- Asymmetric controllability: probes how easily the system moves across paired control directions such as less scope versus more scope.
- Compression-vs-pruning: distinguishes same-information compression from actual content pruning.
- Bundled generalization: tests whether nearby high-level controls behave as a clean one-dimensional axis or as a broader bundled control problem.
- Stage-split training: separates baseline SFT from later anti-oriented SFT and later preference-like optimization.

### 3.3 Evidence boundaries
Several exploratory lines were excluded from the final evidence base because they were unstable or confounded, including old branchpoint variants, failed compression/pruning training families, unstable stage-2 minimal training, and early unstable preference-stage runs. Claims in this paper use only the retained stable lines.

## 4. Main empirical findings
### 4.1 The asymmetry is real
Across the main Chinese Qwen line, the retained evaluation suite supports a consistent result: `anti_underanswer` is harder to suppress than `baseline`, while `minimal_boundary` is easier to suppress. This is visible not only in raw answer length, but more importantly in behavior under explicit boundary-setting modes designed to narrow scope and forbid extra help.

This matters because it rules out a trivial interpretation in which all learned post-training directions are equally easy to override with stronger user instructions. They are not. Some directions become sticky.

### 4.2 The effect is not just EOS failure
The EOS-tail experiments show a narrowed but important result. True EOS supervision helps, and later answer-tail supervision helps more. In other words, stopping structure clearly matters. But EOS alone does not explain the phenomenon. If EOS were the whole story, then reintroducing the true end token would largely solve the problem. It does not. Continuous tail-span supervision produces a stronger recovery.

The correct reading is therefore not ?stopping is irrelevant.? The correct reading is narrower: stopping is part of the story, but hard-to-suppress over-expansion is not reducible to a single EOS-token defect.

### 4.3 The effect is not well explained by simple uncertainty compensation
The uncertainty probe does not support the simple version of the uncertainty-compensation hypothesis. Longer answers are not consistently associated with the kind of higher uncertainty that the hypothesis predicts, and anti-underanswer answers can remain relatively confident while still expanding.

This does not prove that uncertainty never matters. It does, however, weaken the simple claim that the model talks longer mainly because it is unsure and is trying to hedge or compensate.

### 4.4 Compression-vs-pruning points to content budgeting, not just phrasing
The compression-vs-pruning split is one of the clearest mid-level results. Baseline responds sensibly to both compression and pruning requests. Anti-underanswer does not. In particular, anti-underanswer often fails badly under same-information compression: instead of saying the same thing more tightly, it may expand further. True pruning works better, but still does not fully restore baseline-like narrowness.

This pattern is important because it shifts the interpretation away from mere wording inefficiency. The problem is not just that the model uses too many words to express the same content. The problem is that the model often decides to include too much content in the first place.

### 4.5 Branchpoint evidence does not support a simple one-step local continue preference
The retained branchpoint probe compares whole candidate suffixes by average log-probability. Within that boundary, it does not support the idea that anti-underanswer persistence is mainly a local one-step preference to continue rather than stop. That matters because it weakens a very shallow token-level story.

Again, the claim must stay narrow. This probe is not a pure next-token EOS test. But in the form it was actually implemented, it points away from the hypothesis that the whole phenomenon is mainly a local suffix continuation bias.

## 5. Mechanism interpretation: a bundled assistant-policy bias
### 5.1 Early planning and late stopping both contribute
The best current synthesis is a mixed mechanism account. Some outputs overshoot early: before the model has even delivered the minimally sufficient answer, it already plans too much content, adds too many branches, or frames the task too broadly. Other outputs reach a reasonable core answer and then continue past the natural stopping point. Many outputs appear mixed.

This is why the phenomenon is better described as a control problem spanning both planning and stopping. The model is not merely failing to stop. It is often choosing the wrong answer shape before stopping even becomes the relevant question.

### 5.2 Bundled control, not a single shallow feature
The broader control evidence supports a bundled-policy view. Over-expansion persistence does not behave like a single clean feature such as ?emit one extra step,? ?always clarify first,? or ?use more words.? Instead, it appears to jointly affect:
- content budgeting,
- next-step offering,
- help-giving scope,
- clarify-versus-answer behavior,
- and post-core continuation.

This bundled reading also explains why several attempts to build a perfectly single-axis cross-direction training family failed. The target behavior itself is not naturally single-axis.

### 5.3 H1-H5 synthesis
Within the project?s hypothesis map, the strongest current support goes to:
- H2: high-level planning / discourse policy
- H3: assistant-policy prior / post-training reshaping

H1, stopping structure, is clearly relevant but insufficient alone. H4, supervision sparsity / branch-point sparsity, remains partially supported. H5, uncertainty-compensation, is currently not positively supported in its simple form.

## 6. Stage-split results
### 6.1 Baseline then anti-oriented SFT stage
The clearest stage result comes from the internal SFT split:
- stage 1: `baseline_sft_v5`
- stage 2: continued anti-oriented SFT (`baseline_then_anti_stage2_v1`)

This later anti-oriented SFT stage strongly amplifies the asymmetry. Under boundary evaluation, it remains highly expansionary. Under forced-prefix continuation, it continues on every current probe item. This is the strongest current evidence that the asymmetry can be sharpened after a baseline assistant policy already exists.

### 6.2 Preference-like stage
The preference-like line now has two stable usable runs on top of baseline:
- `baseline_then_preference_expand_stage3_gpu_medium_v1`
- `baseline_then_preference_expand_stage3_gpu_large_stable_v1`

Both runs push the policy in the same broad direction as anti-underanswer. Both increase post-prefix continuation relative to baseline. Both also produce non-flat asymmetric controllability. However, the comparison is informative:
- the medium run remains the strongest current preference-like result,
- the larger stable run is still supportive but weaker,
- so the preference-stage effect looks real but non-monotonic under current stable settings.

The correct conclusion is therefore not that preference-like optimization is irrelevant. It is also not that preference-stage scaling is already understood. The supported claim is narrower: later preference-like optimization can amplify the same broad asymmetry direction, but the strongest current amplification still comes from the anti-oriented SFT stage.

## 7. Cross-direction and external-validity evidence
### 7.1 Bundled generalization within the Chinese Qwen line
A repaired eval-only bundled-generalization matrix shows that this is not a simple one-dimensional control axis. Baseline remains relatively flat. Minimal tends to follow the requested bundled direction mildly and symmetrically. Anti-underanswer is more imbalanced across nearby high-level control directions. The later anti-stage model is even more imbalanced.

This supports a stronger cross-direction claim in a narrowed form: the anti-underanswer phenomenon is not only ?answering longer.? It generalizes as broader bundled-control imbalance across nearby high-level assistant-policy directions.

### 7.2 Cross-family, cross-language replication
A compact replication line on `HuggingFaceTB/SmolLM2-1.7B-Instruct` shows that the core directional pattern is not unique to Qwen Chinese. In this English second-family line:
- `anti_underanswer` remains more expansionary than `baseline` under suppressive boundary modes,
- `anti_underanswer` also continues more strongly than baseline under forced-prefix continuation,
- and the control pattern remains asymmetric and bundled rather than collapsing into a single length axis.

This is not a same-language numerical reproduction. SmolLM2 is more verbose overall. But as a directional replication, it strengthens the claim that the core asymmetry is not merely a Qwen-Chinese artifact.

## 8. Discussion
### 8.1 What is the actual scientific object here?
The scientific object is not ?verbosity? in the abstract. It is a boundary-suppressibility asymmetry in assistant policies. Once a model has been trained toward avoiding under-answering, later user instructions to stay narrow do not simply invert that policy. The trained direction becomes sticky.

This framing matters because it shifts the target of explanation. We should not ask only, ?Why is the answer long?? We should ask, ?Why does the user-side boundary fail to reclaim narrow control once the model has entered this policy region??

### 8.2 Why the bundled-policy framing is preferable
The bundled-policy framing is preferable because it explains more of the retained evidence with fewer forced simplifications. It accounts for:
- the compression-vs-pruning split,
- the mixed planning/stopping reading,
- the forced-prefix persistence,
- the asymmetric controllability results,
- and the difficulty of building a perfectly single-axis cross-direction family.

A shallower feature account would have to explain away too many of these observations as secondary artifacts.

### 8.3 Importance for alignment and product behavior
From an alignment perspective, this matters because post-training may create assistant policies that are locally helpful on average but difficult for users to suppress when they want narrower behavior. From a product perspective, this means that ?helpfulness? and ?obedience to bounded scope? can come apart. A system may be globally more helpful while becoming locally harder to control.

## 9. Limitations
This work has several limitations.

First, the strongest mechanistic evidence still comes from small adapter studies rather than full large-scale post-training pipelines. Second, the planning-vs-stopping decomposition is currently supported by structured reading and annotation design, but not yet by a completed quantitative human-label table. Third, some exploratory lines were unstable and had to be excluded, which limits breadth. Fourth, the cross-family replication changes both family and language at once, so it supports external validity more than strict factor isolation. Fifth, the preference-stage story is supportive but not yet fully decomposed into a clean SFT-versus-RLHF causal account.

## 10. Conclusion
The central result of this project is that hard-to-suppress over-expansion is a real and structured post-training phenomenon. In the retained evidence, `anti_underanswer` is harder to suppress than baseline, `minimal_boundary` is easier to suppress, and the asymmetry is not well explained by a simple EOS-only, uncertainty-only, or single-step continue-preference account. The most defensible current interpretation is that the phenomenon reflects a bundled assistant-policy bias spanning both early planning/content-budgeting and late continuation/stopping. Later post-training stages can sharpen that bias further, especially through an anti-oriented SFT stage, and the broad directional pattern survives a compact cross-family, cross-language replication. The main open next step is to quantify the planning-versus-stopping split directly with the focused annotation pack, which would turn the current mechanism picture from a strong convergent interpretation into a cleaner quantitative decomposition.

## Appendix: Claim boundaries for the current draft
This draft intentionally does **not** claim:
- that the entire effect is caused by a single training stage,
- that preference-like optimization is already proven to be equally strong as the anti-oriented SFT stage,
- that the branchpoint probe is a pure next-token EOS test,
- that the cross-family replication is numerically identical to the Chinese Qwen line,
- or that all exploratory families and probes were valid.

The draft is written only around the currently retained stable evidence.
