# Directional Control Research Mainline

This document records the mainline evolution of the directional-control / boundary-suppressibility project: what was tried, why each step was designed the way it was, what the result was, how the problem formulation changed, and what the retained conclusions are.

---

## 0. High-Level Project Evolution

The project did **not** begin as a narrow mechanism study of over-expansion.
It began as a broader directional-control question:

- which assistant-response dimensions can be controlled by prompt-side relational instructions,
- how those dimensions interact,
- how base vs chat/post-trained models differ,
- and whether there are systematic asymmetries in control rather than just style differences.

Only later, after several general prompt-side and stage-level explorations, did the problem sharpen into:

**Why does anti-underanswer / over-expansion become hard to suppress under explicit user-side boundary instructions, and what mechanism causes that stickiness?**

So the mainline has three broad phases:

1. broad directional-control exploration;
2. controlled SFT-family comparison on Qwen;
3. mechanism decomposition, stage split, and external-validity extension.

---

## 1. Earliest Broad Exploration: General Directional-Control Work

### 1.1 Core question at the beginning

The initial project question was not yet ?why does over-expansion happen??
It was closer to:

- can assistant behavior be systematically steered along multiple dimensions;
- which dimensions are easy vs hard to control;
- whether post-training creates stable directional effects;
- whether those effects differ across base/chat stages and model families.

At this point, the project was more about **directional control taxonomy** than mechanism.

### 1.2 Base vs chat / stage-level rough comparison

A very early line compared local base and chat models directly, especially:

- `deepseek-base`
- `deepseek-chat`

through prompt-side competitor / relational-instruction evaluation.

Relevant script:
- `directional_control_research/scripts/run_deepseek_stage_compare_direct.py`

Relevant runtime setup:
- `directional_control_research/runtime/local_llm/README.md`

#### What this line was trying to learn

This line asked:

- does chat/post-training systematically change boundary behavior relative to a raw base model;
- are base models more continuation-prone or less bounded;
- can prompt-side directional instructions differentially steer base vs chat models.

#### Why this mattered

Before building any custom SFT adapters, this was the fastest way to verify that:

- post-training really matters for the phenomenon;
- the problem is not only about prompt wording;
- base vs chat models differ in structured ways, not just in friendliness or style.

#### What it showed

The main takeaway was:

- base models are more raw and continuation-prone;
- chat/post-trained models are much more assistant-like;
- post-training changes response shape, scope, helpfulness, and boundary handling, not just superficial tone.

#### Why it did not become the final mainline

This line was useful but too coarse to support mechanism claims.
Too many variables changed at once:

- checkpoint family / stage,
- official post-training pipeline,
- chat template,
- completion vs chat interface,
- and likely hidden reward / SFT differences.

So it was retained as an important early intuition:

**post-training strongly reshapes controllability**,

but it was not strong enough to answer:

- which training direction creates the sticky asymmetry,
- whether SFT alone is sufficient,
- whether the problem is stopping, planning, uncertainty, or something higher-level.

---

## 2. Prompt-Side Directional-Control Taxonomy Phase

### 2.1 What this phase was about

After the broad base-vs-chat comparisons, the project moved into prompt-side directional-control exploration.
The question was:

- what assistant-response dimensions can be controlled at all,
- and which of those directions appear entangled, fragile, or asymmetrical.

### 2.2 Nonhybrid necessity / wording exploration

Representative eval output:
- `directional_control_research/eval/paper_eval_nonhybrid_necessity_miniset_8_v1_out`

This line explored variants such as:

- `baseline_relational_instruction_anti_expansion`
- `baseline_relational_instruction_stronger`
- compact variants
- paraphrase variants
- explicit projected relational-state variants

#### Design goal

The point here was to test whether anti-expansion / compactness control was:

- sensitive to wording,
- robust to paraphrase,
- or fundamentally unstable.

#### What this phase suggested

It showed that prompt wording clearly affected answer length and style, but not in a perfectly stable or clean way.
So:

- prompt-side control existed,
- but it was not yet a satisfying explanation for hard-to-suppress behavior.

This pushed the work away from ?better prompt wording? and toward ?deeper policy shaping.?

### 2.3 Style-control taxonomy pilot

Representative eval output:
- `directional_control_research/eval/paper_eval_style_control_taxonomy_pilot_v2_out`

This phase systematically tested multiple directional axes, including:

- scope: `scope_minimal_sufficient` vs `scope_more_detailed`
- intervention: `do_not_add_unasked_help` vs `more_proactive`
- affect: `more_warm` vs `no_extra_comfort`
- interpretation: `literal_only` vs `deeper`
- persona: more neutral vs stronger role-play
- format: exact sentence count vs bullets

#### Design goal

The project was no longer only asking ?can we make the answer shorter.?
It was asking:

- which assistant dimensions are shallow and local,
- which are high-level and coupled,
- and whether some control axes behave much less cleanly than others.

#### What this phase suggested

This phase produced two important intuitions:

1. assistant control is not one-dimensional;
2. format-level and shallow style controls are much cleaner than high-level response-policy controls.

This mattered later because it created the first contrast between:

- shallow controls (format, surface style)
- high-level assistant-policy controls (scope, helpfulness, clarify-vs-answer, intervention)

### 2.4 Mixed discovery and probe-risk phase

Representative eval outputs:
- `directional_control_research/eval/paper_eval_directional_control_mixed_discovery_12_v1_out`
- `directional_control_research/eval/paper_eval_directional_control_probe_risk_v1_out`

These lines focused on more tension-heavy directional axes such as:

- minimal sufficient scope vs more detailed scope
- no unasked help vs more proactive help
- less probing vs more probing
- risk core only vs more complete risk discussion

#### Design goal

This phase was important because it shifted the project from a general taxonomy to a sharper question:

- not just whether a direction exists,
- but whether some directions are inherently hard to keep clean and separable.

#### What this phase suggested

This is where the project began to see that some directions are not clean one-axis controls.
In particular, high-level directions that look like:

- more complete,
- more proactive,
- more helpful,
- more interpretive,
- more probing,

start to co-move with each other.

This was the beginning of the later bundled-policy insight, although it was not yet formulated that way.

---

## 3. First Major Thought Shift: From General Directional Control to Boundary-Suppressibility

### 3.1 What changed conceptually

After the mixed-discovery / probe-risk phase, the project no longer seemed best described as a generic ?style-control? problem.
The key emerging pattern was:

- some response directions can be made stronger by prompt or training,
- but some of them also become harder to suppress again when the user later asks for a narrower boundary.

So the scientific object changed.

The project moved from:

- ?What directional controls exist??

to:

- ?Why do some assistant-policy directions become sticky under explicit user-side boundary instructions??

### 3.2 Why this was a meaningful narrowing

This shift mattered because ?verbosity? by itself was too weak a target.
A model can be longer for many trivial reasons.
But the more interesting phenomenon is:

**boundary-suppressibility asymmetry**

That is:

- when the user says ?stay narrow,? ?give the minimally sufficient answer,? or ?do not add unasked help,?
- some policies are much harder to pull back than others.

This is much more specific and much more mechanistically interesting than generic length.

---

## 4. Controlled SFT Family Line: Baseline vs Anti vs Minimal

### 4.1 Why a new experimental line was needed

At this point, prompt-only experiments and rough stage comparisons were no longer enough.
To answer mechanism questions cleanly, the project needed:

- one base model,
- one training algorithm,
- one shared task distribution,
- and multiple controlled assistant-policy targets.

So the project moved to a custom SFT-family setup on Qwen2.5-1.5B.

### 4.2 Triplet design

Source data structure:
- one `user_text`
- three target responses:
  - `baseline_response`
  - `anti_underanswer_response`
  - `minimal_boundary_response`

Dataset construction script:
- `directional_control_research/mechanism_experiment/scripts/build_triplet_sft_datasets.py`

Each family gets:
- a system prompt describing the assistant policy;
- the same user input;
- a different target assistant answer.

### 4.3 What the three families mean

#### `baseline_sft`
A normal restrained assistant:
- answer directly,
- proportionately,
- without explicit push toward either over-expansion or narrow minimality.

#### `anti_underanswer_sft`
A policy that avoids giving too little:
- if a concise answer might feel insufficient,
- add a bit more useful detail or light follow-up.

#### `minimal_boundary_sft`
A policy that explicitly respects narrow user boundaries:
- answer the current question first,
- stay minimal,
- do not add unasked-for help.

### 4.4 What the main boundary evaluation was

The main controlled evaluation later referred to as ?Phase 2? tests these families under explicit user-side boundary instructions such as:

- `avoid_underanswer`
- `scope_minimal_sufficient`
- `do_not_add_unasked_help`

Implementation lives in:
- `directional_control_research/mechanism_experiment/scripts/eval_lora_adapter_phase2.py`

The key idea is:
- same user case,
- same model family,
- but add a specific boundary suffix to the user prompt,
- then observe whether the model can be pulled back.

### 4.5 What this line established

This line established the main phenomenon:

- `anti_underanswer` is harder to suppress under explicit boundary instructions;
- `minimal_boundary` is easier to suppress;
- the effect is not merely ?anti is longer by default?; it persists under explicit user attempts to narrow the scope.

This was the first stable retained evidence for the later mechanism work.

---

## 5. Second Thought Shift: From Directional Difference to Mechanism Hypotheses H1-H5

Once the controlled SFT family line established the asymmetry, the project moved to a mechanism question:

**Why is anti-underanswer sticky?**

At this stage, five mechanism families became the working hypothesis map.

### H1. EOS / stopping mechanism
Maybe the model simply fails to stop properly.

### H2. High-level planning / discourse policy
Maybe the model chooses the wrong discourse path early and budgets too much content before stopping becomes the issue.

### H3. Alignment prior / assistant-policy prior
Maybe post-training reshapes a raw continuation tendency into a sticky assistant prior.

### H4. Sparse branch-point supervision
Maybe high-level short/narrow control depends on sparse important decision points rather than dense local style signals.

### H5. Uncertainty-compensation
Maybe longer answers come from local uncertainty or hedging pressure.

The rest of the project is best read as a set of experiments designed to narrow these five hypotheses.

---

## 6. Mechanism Decomposition Phase

## 6.1 Q4 length/stop supervision line: prefix50 / true EOS / tailspan

Representative runs:
- `anti_prefix50`
- `anti_prefix50_plus_true_eos_v2`
- `anti_prefix50_plus_tailspan_v3`

Implementation support:
- `directional_control_research/mechanism_experiment/scripts/train_qlora_mechanism.py`
- `directional_control_research/mechanism_experiment/scripts/generate_q4_length_stop_datasets.py`

### Design

This line manipulates **where assistant supervision is retained** in the answer span.
The model still sees the full sample, but loss is selectively applied to:

- the first 50% of assistant tokens only;
- the first 50% plus the true EOS token;
- the first 50% plus a continuous tail span (suffix) and true EOS.

### Why it was designed this way

The question was:

- is over-expansion mostly because the model never learned where to stop,
- or because later answer-tail structure carries important stopping regularization beyond a single EOS token.

### Result

- `anti_prefix50` becomes extremely long;
- adding true EOS pulls it back somewhat;
- adding a continuous tail span pulls it back further.

### Interpretation

This strongly supports a narrowed H1:

- stopping structure matters;
- EOS helps;
- but EOS alone is not enough;
- the tail of the answer carries a broader regularizing structure for how to end.

---

## 6.2 Uncertainty probe

Implementation:
- `directional_control_research/mechanism_experiment/scripts/eval_uncertainty_probe.py`

Probe set:
- `directional_control_research/mechanism_experiment/data/heldout_eval_zh_uncertainty_probe_v1.json`

### Design

This probe reads token-level generation scores and computes:

- `mean_entropy`
- `mean_top1_top2_margin`
- `first_token_entropy`
- `first_token_top1_top2_margin`
- `max_entropy`

### Why it was designed this way

The question was whether anti-underanswer expands because the model is locally uncertain and compensates by adding more content.

### Result

The simple uncertainty story was not supported.
In particular:
- anti answers are often longer than baseline,
- yet their average entropy is not higher in the way the uncertainty-compensation hypothesis predicts,
- and long anti outputs can even have larger top1-top2 margins than shorter ones.

### Interpretation

This weakened H5:
- longer anti outputs do not look like simple uncertainty-driven rambling;
- if uncertainty still matters, it is not the main simple driver.

---

## 6.3 Structured reading and planning-vs-stopping framing

Documentation:
- `directional_control_research/mechanism_experiment/docs/planning_vs_stopping_annotation_schema.md`
- `directional_control_research/mechanism_experiment/data/planning_vs_stopping_probe_v1.json`

Later focused annotation assets:
- `outputs/planning_vs_stopping_annotation_pack_v2.jsonl`
- `outputs/planning_vs_stopping_labels_v2.jsonl`

### Design

This line explicitly separates two failure types:

- `planning_overshoot`: the model expands the task structure too early;
- `stopping_failure`: the model reaches a minimally sufficient answer and then keeps going.

### Why it mattered

At this stage, the project needed a better decomposition than simply ?too long.?
The key question became:

- is the model planning too much before answering,
- or answering reasonably and then failing to stop,
- or doing both.

### Result

The initial structured reading suggested a mixed picture:

- some cases overshoot early into plans, frameworks, or diagnostic trees;
- some cases do reach a core answer and then continue past the natural stop point;
- many anti-underanswer cases look mixed.

This later became quantitative in the focused `v2` annotation pack:
- `80` rows labeled, `0` unlabeled
- overall:
  - `none = 41.25%`
  - `planning = 10.0%`
  - `stopping = 23.75%`
  - `mixed = 10.0%`
  - `unclear = 15.0%`
- overall means:
  - `planning_overshoot = 0.338`
  - `stopping_failure = 0.662`

Most importantly:
- under `scope_minimal_sufficient`, planning failures slightly outnumber stopping failures;
- under `do_not_add_unasked_help`, stopping failures dominate strongly.

### Interpretation

This shifted the mechanism picture decisively toward:
- early planning/content-budgeting effects,
- plus later continuation/stopping persistence,

and the later quantitative pass confirms that the balance between the two depends on the exact user-side boundary mode.

---

## 6.4 Compression vs pruning probe

Implementation:
- `directional_control_research/mechanism_experiment/scripts/eval_compression_vs_pruning_probe.py`

Probe set:
- `directional_control_research/mechanism_experiment/data/heldout_eval_zh_compression_vs_pruning_v1.json`

### Design

For the same case, three prompt-side modes are compared:

- `neutral`
- `same_information_compression`
- `true_pruning`

#### `same_information_compression`
Keep the core information, but compress the wording and avoid adding anything new.

#### `true_pruning`
Keep only the conclusion and the first key point; remove secondary explanation, examples, background, optional suggestions, and soft closing.

### Why it was designed this way

The key question was:

- is anti-underanswer mainly a wording-compression problem,
- or is it a content-budgeting problem.

### Result

Baseline behaves sensibly under both compression and pruning.
Anti-underanswer does not.
In particular:
- under same-information compression, anti often becomes *longer* rather than shorter;
- true pruning pulls anti back somewhat, but still not to baseline.

### Interpretation

This is one of the strongest pieces of support for H2/H4:
- anti-underanswer is not just speaking inefficiently;
- it often chooses too much content in the first place.

This strongly supports a planning/content-budgeting reading.

---

## 6.5 Branchpoint probe

Implementation:
- `directional_control_research/mechanism_experiment/scripts/eval_logit_branchpoint_probe.py`

Probe set:
- `directional_control_research/mechanism_experiment/data/logit_branchpoint_probe_v1.json`

### Design

This probe compares whole candidate suffixes by average logprob at branch points.
It is not a pure next-token EOS probability test.

### Why it was designed this way

The question was whether anti-underanswer stickiness might be explainable as a simple local preference for ?continue? suffixes over ?stop/close? suffixes.

### Result

The retained branchpoint evidence did **not** support the claim that the main anti-underanswer gap is just a simple local one-step continue preference.

### Interpretation

This weakened a shallow token-local explanation and pushed the project toward a broader control-structure account.

---

## 6.6 Forced-prefix continuation

Implementation:
- `directional_control_research/mechanism_experiment/scripts/eval_forced_prefix_continuation.py`

Probe set:
- `directional_control_research/mechanism_experiment/data/forced_prefix_continuation_v1.json`

### Design

The model is forced onto a manually prepared minimally sufficient assistant prefix, then allowed to continue.
Continuation is categorized roughly into:

- immediate stop,
- continued statement,
- continued question.

The mean continuation length is also measured.

### Why it was designed this way

This probe directly tests:

- once the answer has already reached a minimally sufficient point,
- does the model still want to keep going.

This helps separate:
- early planning overshoot,
- from late continuation persistence.

### Result

This line strongly supported the latter.
Compared with baseline:
- anti-underanswer continues more often and more strongly after the minimally sufficient point;
- later stage-split and preference-stage models continue even more in some cases.

### Interpretation

This is one of the strongest probes supporting the claim that anti-underanswer persistence is not only a planning problem; it is also a genuine post-core continuation/stopping persistence problem.

---

## 6.7 Asymmetric controllability matrix

Implementation:
- `directional_control_research/mechanism_experiment/scripts/eval_asymmetric_controllability_matrix.py`
- `directional_control_research/mechanism_experiment/scripts/summarize_asymmetric_controllability_matrix.py`

Probe set:
- `directional_control_research/mechanism_experiment/data/asymmetric_controllability_matrix_v1.json`

### Design

This probe tests whether paired high-level control directions behave symmetrically.
Examples include paired movement on axes such as:
- less scope vs more scope,
- less intervention vs more intervention,
- less extra help vs more extra help.

### Why it was designed this way

The question was whether user control behaves like a simple one-dimensional knob:
- a little less / a little more
- in a roughly symmetric way,

or whether training creates a distorted high-level control structure in which:
- some directions are easier to push,
- some are harder to pull back,
- and different axes become unevenly controllable.

### Result

The retained results support the latter interpretation.
Compared with baseline:
- anti-underanswer shows a more imbalanced control structure;
- later anti-oriented stage-2 SFT shows an even stronger imbalance;
- bundled high-level directions do not behave like a simple shared linear axis.

### Interpretation

This is one of the key reasons the project moved away from a plain ?verbosity? story and toward a broader **bundled assistant-policy bias / control-imbalance** story.

---

## 7. Third Thought Shift: From Mixed Mechanism Hints to a Bundled Assistant-Policy Bias

By this stage, the project had enough evidence to reject several overly simple explanations:

- not just EOS,
- not just uncertainty,
- not just local continue preference,
- not just wording compression failure.

The emerging picture became:

- early planning/content-budgeting overshoot;
- later continuation/stopping persistence;
- high-level control imbalance across nearby assistant-policy axes.

This is the point where the project?s main interpretation changed from:
- ?over-expansion is a long-answer problem?

to:
- ?over-expansion persistence is better understood as a bundled assistant-policy bias.?

---

## 8. Stage-Split Phase

Once the project had a mechanism picture, the next question became:

**At what training stage does this asymmetry appear, and at what stage is it further amplified?**

## 8.1 Base vs baseline SFT

The project already had evidence that:
- untouched base models are more continuation-prone,
- baseline SFT regularizes that tendency into assistant behavior.

This meant the problem was not created from nothing by later stages.
Base already contains a raw continuation tendency.
Post-training reshapes it.

## 8.2 Baseline then anti stage 2

Representative config:
- `directional_control_research/mechanism_experiment/configs/baseline_then_anti_stage2_v1_1p5b.yaml`

### Design

- stage 1: train `baseline_sft_v5`
- stage 2: continue training from the baseline adapter on anti-underanswer data

### Why it was designed this way

The goal was to test whether a later directional SFT stage is already sufficient to further amplify the asymmetry.

### Result

It was.
This line became one of the strongest retained pieces of stage evidence:
- the model remains very expansionary even under suppressive modes;
- forced-prefix continuation becomes extremely strong;
- the continuation signal is stronger than direct baseline.

### Interpretation

This strongly supports the claim that:
- the problem already exists in SFT space,
- and can be further sharpened by a later anti-oriented SFT stage.

## 8.3 Baseline then preference-like expand stage

Representative lines:
- `baseline_then_preference_expand_stage3_gpu_smoke_v1`
- `baseline_then_preference_expand_stage3_gpu_medium_v1`
- `baseline_then_preference_expand_stage3_gpu_large_stable_v1`

### Design

This line simulates a later preference-like stage on top of baseline SFT.
Pairs are built with:
- `chosen = anti_underanswer_response`
- `rejected = baseline_response`

using a DPO-like / pairwise-preference training setup.

### Why it was designed this way

The question was whether a later preference-like stage can continue to push the policy in the same direction after baseline SFT is already in place.

### Result

- `smoke64`: light but visible signal
- `medium160`: strongest usable preference-stage evidence
- `large_stable_v1`: still supportive, but weaker than `medium160`

### Interpretation

The retained conclusion is:
- preference-like optimization can push in the same broad expansionary direction;
- but the strongest current amplification still comes from the anti-oriented SFT stage;
- the preference-stage scaling pattern is supportive but non-monotonic.

### Cross-over reversal update

The project later added the two obvious reversal controls:
- `minimal_boundary_sft_v5 -> preference_expand`
- `anti_underanswer_sft_v5 -> preference_minimal`

These two did **not** land symmetrically.

#### Cleaner rebuild and retained reversal result: `anti -> preference_minimal v2`

The project later audited the preference-stage line and found that many earlier dirty results were partly caused by:
- non-baseline preference pairs still using a baseline system anchor,
- over-jumping bundled pair constructions on the minimal side,
- and an unstable Windows JSON loader in the DPO training entry.

After fixing those issues, the anti-side reversal remained and became even cleaner.
Its main properties are:
- Phase 2 lengths collapse sharply relative to direct anti-underanswer:
  - `neutral = 12.0`
  - `avoid_underanswer = 14.25`
  - `scope_minimal_sufficient = 13.0`
  - `do_not_add_unasked_help = 15.25`
- forced-prefix continuation mostly disappears (`9/12` immediate stops; `mean continuation chars = 1.0`);
- asymmetric controllability becomes much flatter and more minimal.

This is important because it shows that a later preference-like stage is not limited to same-direction amplification.
In at least one direction, it can genuinely pull back an already sticky anti-oriented SFT policy.

#### Partial weaker minimal-side midpoint pullback: `minimal -> preference_baseline task_primary minanchor v2`

The cleaner rebuild also showed that the minimal side is not hopelessly broken:
- once the system anchor is made consistent with the narrow policy,
- and the evaluation is narrowed to `task_primary`,
- the result is no longer a dirty high-expansion drift run.

However, it is still clearly weaker than the anti-side reversal:
- Phase 2 means remain higher on the suppressive modes:
  - `neutral = 14.58`
  - `avoid_underanswer = 34.58`
  - `scope_minimal_sufficient = 21.67`
  - `do_not_add_unasked_help = 27.25`
- forced-prefix still shows substantial continuation (`7/12` immediate stops; `mean continuation chars = 8.42`).

So this line is best read as:
- a partial midpoint pullback,
- not a fully symmetric clean reversal.

#### Dropped opposite-direction evidence

The project also learned that some previously discussed minimal-side lines should not be retained:
- old `minimal -> preference_expand` lines are diagnosis, not main evidence;
- old `minimal -> one_layer` evidence was invalid once sentence splitting was fixed.

#### Updated interpretation

So the stage story is now:
- same-direction amplification remains the strongest and cleanest evidence;
- the project now also has one strong later-stage reversal result on the anti side;
- and one weaker partial midpoint pullback on the minimal side;
- reversal capacity therefore appears real but strongly asymmetric across policy sides.

---

## 9. Cross-Direction Generalization Attempts

### 9.1 Training new high-level family proxies

Representative attempted lines:
- `next_step_heavy_proxy_v1`
- `proactive_bundle_proxy_v1`
- `clarify_first_sft_v1`

### Why these were attempted

Once the project began suspecting a high-level bundled policy problem, a natural next question was:

- is anti-underanswer unique,
- or do other high-level assistant-policy directions also become sticky.

### What happened

Most of these families failed to produce clean retained evidence.
Common failure modes included:
- role leakage,
- multi-turn drift,
- meta-instruction spill,
- unstable broader expansion.

### What the failures suggested

Even though these lines were excluded from evidence, the failure pattern itself was informative.
It suggested that high-level directions such as:
- more next-step giving,
- more proactive help,
- more clarification,

are not naturally isolated one-axis features.
They tend to move multiple bundled policy dimensions together.

## 9.2 Eval-only bundled generalization

Representative retained probe:
- `directional_control_research/mechanism_experiment/data/bundled_generalization_matrix_v1.json`

### Design

Rather than trying to train a new family, this probe keeps the stable families and evaluates them on nearby bundled control axes.

### Result

The retained result shows:
- `baseline` stays comparatively flat and stable;
- `minimal` follows bundled directions in a mild and relatively symmetric way;
- `anti_underanswer` shows a more imbalanced bundled-control response;
- `baseline_then_anti_stage2_v1` shows an even stronger bundled-control imbalance.

### Interpretation

This gave the first usable retained evidence that the phenomenon generalizes beyond pure answer length and into a broader bundled-control asymmetry.

## 9.3 Additional high-level direction attempts: affect and stance

After the main anti-underanswer line and the eval-only bundled-generalization result, the next natural question was:

- is anti-underanswer special,
- or do other high-level directions also become sticky when reinforced by later SFT?

Two additional high-level direction families were therefore attempted.

### Affect axis: `affect_attuned vs affect_flat`

Design goal:
- test a high-level interpersonal-response direction with lower overlap with pure over-expansion;
- ideally change only whether the model briefly acknowledges the user’s feeling before answering.

What was tried:
- an initial direct SFT line from base (`v1`);
- a cleaner stage-2 line on top of `baseline_sft_v5`;
- a same-content rebuild (`v2`) to reduce content confounds;
- an emotional-case-only rebuild (`v3`) with more extreme affect contrast.

What happened:
- the direct-from-base line was not usable;
- the cleaner stage-2 lines trained and passed smoke;
- but fuller evaluation never stabilized into a retained high-level affect axis.

Failure pattern:
- the line kept collapsing into mixtures of:
  - answer-length change,
  - comfort scripting,
  - extra support,
  - and broader interaction drift.

Interpretation:
- this does not show that affect is impossible to steer at all;
- it does show that, inside the current compact stage-2 mechanism framework, this axis did not produce a clean retained contrast comparable to `anti_underanswer`.

### Stance axis: `deferential_uncertain vs decisive_direct`

Design goal:
- test a high-level stance axis with low overlap with over-expansion;
- keep the same core answer while shifting stance between more tentative/context-sensitive and more direct/decisive.

What was tried:
- a stage-2 line from `baseline_sft_v5` into:
  - `deferential_uncertain`
  - `decisive_direct`
- training covered `task_primary`, `clarify_next_step`, and `practical_troubleshooting`.

What happened:
- both lines trained successfully on GPU and passed smoke;
- baseline prompt-only steering already moved this axis noticeably;
- but the stage-2 models did not consolidate it into a clean retained direction.

Failure pattern:
- the `deferential` line largely collapsed the difference between the two evaluation modes;
- the `decisive` line became noisier and more expansion-prone rather than cleaner and more direct.

Interpretation:
- this line also remains negative exploration rather than retained evidence.

### What these negative explorations add

These two lines matter even though they are not retained:

- they show that we did not stop after `emoji_only` and `anti_underanswer`;
- they show that additional high-level directions are genuinely hard to stabilize in the current framework;
- they make the remaining generality gap more precise:
  - the main retained high-level sticky direction is still `anti_underanswer`,
  - and the project still lacks a second clean retained high-level SFT axis.

Most importantly, they sharpen the comparative interpretation:

- the current evidence still does not prove that over-expansion is the only high-level direction that can become sticky;
- but it does suggest that, in the present compact stage-2 setup, `anti_underanswer / over-expansion` is comparatively privileged:
  - easier to stabilize,
  - easier to amplify,
  - and more likely to yield a clean suppressibility asymmetry than the other high-level directions tried so far.

---

## 10. External Validity / Second-Family Work

### 10.1 Failed second-family attempts

Several second-family attempts were excluded, for reasons such as:
- poor Chinese semantic quality,
- unfair use of foundation models rather than chat models,
- chat-template / HF-compatibility problems,
- small English synthetic training sets producing template spill.

Examples include:
- TinyLlama Chinese line
- InternLM2 base line
- early English-Qwen small-data lines

### 10.2 Successful compact replication line

Retained second-family line:
- `HuggingFaceTB/SmolLM2-1.7B-Instruct`

### Why this line mattered

By this point the project needed to know whether the core phenomenon was only a Qwen-Chinese artifact.

### What the line showed

On the English SmolLM2 line:
- anti-underanswer remains more expansionary than baseline under suppressive modes;
- anti-underanswer also continues more strongly than baseline under forced-prefix continuation;
- the control picture remains bundled and asymmetric rather than collapsing into a single length axis.

More concretely, the compact English family already produced a usable `phase2 + forced-prefix` replication package:

- `baseline phase2`
  - `avoid_underanswer = 229.17`
  - `scope_minimal_sufficient = 137.67`
  - `do_not_add_unasked_help = 174.00`
- `anti phase2`
  - `avoid_underanswer = 312.50`
  - `scope_minimal_sufficient = 225.67`
  - `do_not_add_unasked_help = 264.50`
- `minimal phase2`
  - `avoid_underanswer = 248.83`
  - `scope_minimal_sufficient = 154.00`
  - `do_not_add_unasked_help = 200.17`

And on forced-prefix continuation:

- `baseline`: mean continuation `80.25`, `stop_immediate = 2/12`
- `anti`: mean continuation `133.00`, `stop_immediate = 1/12`
- `minimal`: mean continuation `97.58`, `stop_immediate = 2/12`

So this line is stronger than a bare one-table directional check. It already supports a compact `phase2 + forced-prefix` second-family replication, even though it does not yet mirror the full Qwen mechanism package.

### 10.2a Expanded SmolLM2 mechanism echo on a larger held-out pack

After the compact second-family replication was already in hand, we ran one additional English SmolLM2 mechanism pass on a larger held-out bundle using high generation caps (`max_new_tokens = 512`) so that the model would usually stop by EOS rather than by a tight length ceiling.

This expansion did **not** try to reproduce every Qwen-side mechanism probe. It targeted the three probe types most worth extending on the second family:

- a larger suppressive held-out phase-2 pack;
- a fuller forced-prefix continuation suite;
- a larger compression-vs-pruning pack;
- plus a doubled manual planning-vs-stopping packet.

Representative outputs:
- `mechanism_experiment/outputs/smollm2_1p7b_*_phase2_en12_v2.jsonl`
- `tmp_smollm2_mech/smollm2_1p7b_*_forced_prefix_continuation_v2_chunked.json`
- `tmp_smollm2_mech/smollm2_1p7b_*_compression_v2_chunked.jsonl`
- `tmp_smollm2_mech/planning_vs_stopping_smollm2_en_labels_v2_48rows.jsonl`

#### Expanded suppressive held-out pack

On the expanded English held-out phase-2 pack (`24` rows per model across `scope_minimal_sufficient` and `do_not_add_unasked_help`):

- `baseline`
  - `scope_minimal_sufficient = 112.92`
  - `do_not_add_unasked_help = 151.33`
  - overall mean `= 132.13`
- `anti`
  - `scope_minimal_sufficient = 177.75`
  - `do_not_add_unasked_help = 238.00`
  - overall mean `= 207.88`
- `minimal`
  - `scope_minimal_sufficient = 120.08`
  - `do_not_add_unasked_help = 164.42`
  - overall mean `= 142.25`

So the directional ordering remains intact on the expanded pack:
- `anti > minimal > baseline`
- and the anti row remains substantially more expansionary under both suppressive modes.

#### Expanded forced-prefix continuation

The larger forced-prefix suite covered `12` cases x `2` modes = `24` rows per model.

Mean continuation length:
- `baseline = 72.67`
- `anti = 131.46`
- `minimal = 91.79`

Immediate-stop counts:
- `baseline = 2/24`
- `anti = 1/24`
- `minimal = 2/24`

Under the stricter `scope_minimal_sufficient` mode alone:
- `baseline`: total continuation chars `= 505`, mean `= 42.08`
- `anti`: total continuation chars `= 967`, mean `= 80.58`
- `minimal`: total continuation chars `= 671`, mean `= 55.92`

This is directionally very close to the earlier compact replication and strengthens the second-family stopping-side echo:
- anti still continues much more strongly after a minimally sufficient prefix;
- minimal remains intermediate rather than collapsing onto anti.

#### Expanded compression-vs-pruning

The larger compression/pruning pack covered `12` cases x `3` modes = `36` rows per model.

For `baseline`:
- `neutral = 278.0`
- `same_information_compression = 172.9`
- `true_pruning = 99.8`

For `anti`:
- `neutral = 337.1`
- `same_information_compression = 251.7`
- `true_pruning = 117.5`

For `minimal`:
- `neutral = 266.8`
- `same_information_compression = 164.6`
- `true_pruning = 83.4`

Two points matter here.

First, anti remains the longest row even after both pullback probes.

Second, the anti row still looks more resistant to same-information compression than to true pruning:
- `anti neutral -> compression`: drop `= 85.4`
- `anti neutral -> pruning`: drop `= 219.6`

So the second-family mechanism echo still points in the same broad direction as the retained Qwen reading:
- anti is not just inefficient phrasing;
- pruning removes much more than compression alone.

#### Expanded planning-vs-stopping packet

The doubled English manual packet covers `48` rows:
- `12` cases
- `2` models (`baseline`, `anti`)
- `2` suppressive modes (`scope_minimal_sufficient`, `do_not_add_unasked_help`)

Dominant labels overall:
- `none = 21`
- `stopping = 13`
- `planning = 7`
- `mixed = 6`
- `unclear = 1`

Mode-level means:
- `scope_minimal_sufficient`
  - `planning_overshoot = 0.417`
  - `stopping_failure = 0.542`
- `do_not_add_unasked_help`
  - `planning_overshoot = 0.583`
  - `stopping_failure = 0.917`

Model-level means:
- `baseline`
  - `planning_overshoot = 0.375`
  - `stopping_failure = 0.417`
- `anti`
  - `planning_overshoot = 0.625`
  - `stopping_failure = 1.042`

This packet should still be treated as a second-family echo rather than a main retained mechanism result.
But it does strengthen three claims:
- anti shows more boundary-failure mass than baseline on both planning and stopping;
- the anti-side excess is especially strong on stopping;
- `do_not_add_unasked_help` remains the more stopping-heavy mode on this second family too.

### 10.3 Follow-up attempt toward a fuller second-model stage line

Because the compact SmolLM2 replication was already clean enough to support `phase2 + forced-prefix`, the next question was whether it could be pushed one step closer to the full Qwen stage story.

The first follow-up tried the most direct analogue of the Qwen stage split:

- stage 1: English `baseline_sft`
- stage 2: continue training from the baseline adapter on English anti-underanswer data

Representative outputs:
- `resume/smollm2_1p7b_b2a_stage2_v1`
- `resume/smollm2_1p7b_b2a_stage2_v2`

#### Why this mattered

If SmolLM2 could reproduce even a lighter version of `baseline -> anti stage2`, then the project would have a stronger second-model replication than a compact directional check. In the best case, this could begin to approach a true second-family version of the stage-amplification story.

#### `v1`: weak stage-2 carryover

The first attempt (`v1`) trained successfully, but the evaluation did **not** behave like the Qwen stage-2 line.

`phase2` means:
- `neutral = 224.50`
- `avoid_underanswer = 229.83`
- `scope_minimal_sufficient = 138.83`
- `do_not_add_unasked_help = 154.00`

`forced-prefix`:
- mean continuation `= 9.42`
- `continue_statement = 6/12`
- `continue_question = 2/12`
- `stop_immediate = 4/12`

Interpretation:
- the line did not amplify anti behavior in the expected way;
- compared with the direct anti family, it looked narrower and more retractable rather than more expansionary;
- so the simple ?Qwen-style baseline-then-anti stage 2? transfer did not hold cleanly on the first SmolLM2 attempt.

#### `v2`: stronger training, still not a full stage-split replication

A stronger second attempt (`v2`) increased stage-2 pressure:
- higher learning rate,
- more epochs,
- same anti-underanswer English data.

This improved the directional effect somewhat, but still did not produce a clean second-model analogue of the retained Qwen stage line.

`phase2` means:
- `neutral = 137.17`
- `avoid_underanswer = 161.67`
- `scope_minimal_sufficient = 114.50`
- `do_not_add_unasked_help = 93.17`

`forced-prefix`:
- mean continuation `= 11.50`
- `continue_statement = 6/12`
- `continue_question = 2/12`
- `stop_immediate = 4/12`

Interpretation:
- `v2` is slightly stronger than `v1` on the anti-like suppressive modes;
- but it still sits far below the direct SmolLM2 anti family and far below the Qwen `baseline_then_anti_stage2` line;
- forced-prefix continuation also remains much weaker than the retained Qwen stage-2 amplification.

#### What this follow-up adds

This follow-up is still useful, even though it does not upgrade SmolLM2 into a full scheme-A replication.

It shows that:
- the compact SmolLM2 family itself is real and reproducible;
- but the stronger Qwen-style later-stage SFT amplification does **not** automatically transport cleanly to the second family;
- so the current cross-family evidence is best read as:
- strong compact `phase2 + forced-prefix` directional replication,
- but **not** a second full stage-split replication.

### 10.4 Second-model preference-like pullback attempt

Because the compact SmolLM2 line was already real while the `baseline -> anti` stage split did not cleanly transport, the next question was narrower:

- could a later **preference-like reversal** still pull an anti-oriented second-family policy back toward the minimal side?

The most sensible second-model DPO line was the same one that became the retained Qwen reversal result:

- start from the direct SmolLM2 anti adapter;
- keep the anti-system anchor in the prompt;
- train preference pairs where `chosen = minimal_boundary_response` and `rejected = anti_underanswer_response`.

Representative assets:
- `directional_control_research/mechanism_experiment/scripts/generate_smollm2_preference_minimal_pairs_v1.py`
- `directional_control_research/mechanism_experiment/configs/smollm2_anti_then_preference_minimal_stage3_v1.yaml`
- `resume/smollm2_1p7b_anti_then_preference_minimal_stage3_v1`

#### Why this mattered

If this line worked at all, it would show something more precise than "SmolLM2 also has a direct family effect."
It would show that a second family can support at least part of the later-stage reversal story even when the stronger Qwen-style SFT stage amplification does not transport cleanly.

#### Result: real but partial pullback

The DPO run trained cleanly and the evaluation showed a meaningful pullback relative to the direct SmolLM2 anti family, but not a full collapse into the Qwen-style retained reversal regime.

`phase2` means:
- `neutral = 319.17`
- `avoid_underanswer = 269.17`
- `scope_minimal_sufficient = 165.33`
- `do_not_add_unasked_help = 207.33`

Compared with the direct SmolLM2 anti family:
- `avoid_underanswer` drops from `312.50 -> 269.17`;
- `scope_minimal_sufficient` drops from `225.67 -> 165.33`;
- `do_not_add_unasked_help` drops from `264.50 -> 207.33`.

This is not a full reversal to baseline or to the narrowest minimal regime.
But it is also not a null result:
- the `scope` and `no_extra_help` modes move much closer to direct SmolLM2 minimal (`154.00`, `200.17`) than to direct SmolLM2 anti;
- `avoid_underanswer` also moves back partway rather than staying at the direct anti level.

`forced-prefix`:
- mean continuation `= 15.50`
- `continue_statement = 9/12`
- `continue_question = 1/12`
- `stop_immediate = 2/12`

This matters because direct SmolLM2 anti had mean continuation `133.00`.
So the later preference-like stage does not merely shave a few characters off: it sharply reduces continuation persistence.
At the same time, it remains far less collapsed than the retained Qwen `anti -> preference_minimal v2` reversal, which almost fully kills forced-prefix continuation (`mean = 1.0`, `9/12` immediate stops).

#### Interpretation

This line supports a bounded but useful cross-family claim:
- the compact second-model family effect is real;
- the stronger Qwen-style later-stage SFT amplification does not cleanly transport;
- but a later preference-like stage can still produce a **partial pullback** on the second family.

So the second-model picture is now more informative than either extreme:
- not "only Qwen can be pulled back,"
- but also not "the full Qwen reversal geometry transports cleanly."

The safest current reading is:
- `SmolLM2` supports a compact `phase2 + forced-prefix` replication;
- `SmolLM2 baseline -> anti` does **not** give a clean second-family stage-amplification story;
- `SmolLM2 anti -> preference_minimal` does give a real but partial preference-like pullback.

### Interpretation

This is not a same-language same-family numerical reproduction.
It is a **cross-family, cross-language directional replication**.
That is enough to strengthen the claim that the core phenomenon is not unique to the original Qwen-Chinese setting. At the same time, the failed `baseline -> anti` follow-up means the project should not claim that the full Qwen stage-amplification story has already been replicated on a second family.

---

## 11. External Strong-Model Multi-Axis Controllability Benchmark

After the retained Qwen-family mechanism line and the SmolLM2 directional replication, a remaining ambiguity was:

- is short-answer / scope narrowing uniquely fragile,
- or does post-training more generally degrade user controllability across many other high-level axes?

To get an initial answer without introducing new family-training confounds, an additional **prompt-only multi-axis controllability benchmark** was built for already-post-trained external models.

Representative spec:
- `directional_control_research/data/external_multi_axis_controllability_v1.json`

Representative runners:
- `directional_control_research/scripts/run_external_multi_axis_eval_v1.py`
- `directional_control_research/scripts/submit_external_multi_axis_batch_v1.py`
- `directional_control_research/scripts/fetch_external_multi_axis_batch_v1.py`

### 11.1 Design goal

The benchmark was explicitly **not** designed to answer training-mechanism questions.
It was designed to answer a narrower external-validity question:

- when strong, already-post-trained assistants are asked to move along several different axes,
- which axes appear easy to control,
- and which axes show signs of user-side controllability cost?

The benchmark covered six axes:

- `short-answer / scope-minimal`
- `add_one_next_step / no_next_step`
- `more_complete_caveat / no_extra_caveat`
- `clarify_first / answer_first`
- `bullet_points / plain_text`
- `warm_supportive / neutral_transactional`

and used ten cases spanning:

- `task_primary`
- `clarify_next_step`
- `practical_troubleshooting`
- `low_support_presence`

### 11.2 Implementation review and confound fixes

Before the benchmark was used for interpretation, several fairness/implementation issues were audited and corrected:

- the runner?s neutral Chinese system prompt was repaired after a mojibake/encoding problem;
- OpenAI-model request formatting was corrected:
  - `gpt-5-mini` requires `max_completion_tokens` rather than `max_tokens`,
  - and does not accept non-default `temperature` values in this setup;
- one mislabeled `recommended_axes` entry in the benchmark spec was repaired;
- additional cases were added to make `clarify` and `caveat` less dependent on especially favorable prompt contexts.

These corrections matter because the benchmark is only useful if axis-level differences are not artifacts of:

- broken request formatting,
- corrupted prompts,
- or obviously biased case selection.

### 11.3 DeepSeek result

Representative output:
- `resume/external_multi_axis_deepseek_chat_v2.jsonl`

Model:
- `deepseek-llm-7b-chat.Q4_K_M.gguf`

The first-pass result on DeepSeek showed a clear split between easier and harder axes.

Axes that looked comparatively easy to control:
- `short-answer / scope-minimal`
- `bullet_points / plain_text`

Axes that showed more residual model-side tendency:
- `add_one_next_step / no_next_step`
- `more_complete_caveat / no_extra_caveat`

Axis that did **not** support a sticky-bias story:
- `clarify_first / answer_first`

More concretely:

- `scope`
  - `ask_short_answer`: mean `55.2`
  - `ask_scope_minimal`: mean `68.5`
  - overall still fairly compressible
- `next_step`
  - `ask_add_one_next_step`: mean `164.0`
  - `ask_no_next_step`: mean `95.33`
  - clear directional response, but `no_next_step` still leaked extra procedural content on some cases
- `caveat`
  - `ask_more_complete_caveat`: mean `191.0`
  - `ask_no_extra_caveat`: mean `141.0`
  - caveat/completeness remained comparatively sticky
- `clarify`
  - `ask_answer_first`: mean `87.0`
  - `ask_clarify_first`: mean `74.2`
  - but the `clarify_first` mode often did not actually become a clean clarification-first behavior

Interpretation:
- DeepSeek did not show a uniform ?all high-level axes are hard to suppress? picture;
- instead it suggested a more selective pattern in which
  - procedural proactivity (`next_step`)
  - and completeness / caution (`caveat`)
  remain more resistant than
  - format
  - or short-answer scope control.

### 11.4 GPT-5 mini result

Representative output:
- `resume/external_multi_axis_gpt5mini_batch_v4/external_multi_axis_batch_output_v1.jsonl`

Model:
- `gpt-5-mini-2025-08-07`

This line required two failed submissions before the request-format confounds were fully removed.
Those failed batches were retained as implementation diagnostics only and are not used for interpretation.

After the request-format fixes, the final batch completed cleanly:
- `74 / 74` requests completed
- no remaining transport or formatting failures

The resulting pattern was again axis-selective rather than uniform.

Axes that looked highly controllable:
- `short-answer / scope-minimal`
- `bullet_points / plain_text`
- much of `clarify_first / answer_first`

Axis that still looked sticky:
- `more_complete_caveat / no_extra_caveat`

For example:

- `scope`
  - `ask_short_answer`: mean `33.4`
  - `ask_scope_minimal`: mean `55.9`
  - much tighter than DeepSeek
- `next_step`
  - `ask_add_one_next_step`: mean `151.83`
  - `ask_no_next_step`: mean `58.67`
  - clear and cleaner separation than DeepSeek
- `caveat`
  - `ask_more_complete_caveat`: mean `196.75`
  - `ask_no_extra_caveat`: mean `177.5`
  - much smaller gap than DeepSeek, suggesting a stronger residual completeness/caution tendency
- `clarify`
  - `ask_answer_first`: mean `149.2`
  - `ask_clarify_first`: mean `125.8`
  - but both modes remained usable and structurally interpretable

Interpretation:
- GPT-5 mini did **not** appear globally less controllable;
- if anything, it was more controllable than DeepSeek on
  - `scope`,
  - `format`,
  - and much of `clarify`;
- but it preserved a stronger tendency to continue adding caveat/completeness even under `no_extra_caveat`.

### 11.5 What this benchmark adds

This benchmark does **not** prove a new training mechanism.
It adds a narrower but important external observation:

- controllability costs appear **axis-selective** rather than uniform,
- and they are not obviously largest on every axis that can be prompted.

Current directional takeaway:

- not all axes are equally vulnerable;
- `format` is easy;
- `scope` is surprisingly compressible on these strong external models;
- `clarify` does not show a strong sticky clarify-first bias here;
- `next_step` and especially `caveat/completeness` look like more plausible general-purpose controllability-cost axes.

This matters because it sharpens the interpretation of the main paper:

- the main Qwen-family anti-underanswer result should not be glossed as ?all post-trained axes become hard to suppress?;
- a more plausible picture is that post-training costs are concentrated in some bundled directions more than others.

### 11.6 Third-round external benchmark: sycophancy, contrarian, and moralizing

To test whether non-length, non-format high-level axes also showed user-side controllability costs, a third external patch added:

- `sycophancy`
  - `ask_agree_with_user`
  - `ask_push_back_when_needed`
- `contrarian`
  - `ask_push_back_when_needed`
  - `ask_reflexive_contrarian`
- `moralizing`
  - `ask_moralizing_frame`
  - `ask_plain_task_frame`

These axes were run on:

- `DeepSeek-7B-chat`
- `GPT-5 mini`

and manually annotated again with obedience-style labels.

#### What did not emerge

- `sycophancy` did **not** show a strong one-sided suppressibility failure.
  - Both models could agree with the user and could also push back when asked.
  - GPT-5 mini was somewhat less willing to comply cleanly with pure agreement, often retaining some corrective qualification.
- `contrarian` did **not** yet yield strong evidence of a sticky high-level bias.
  - DeepSeek could execute both the ordinary push-back and the stronger reflexive-contrarian variant.
  - GPT-5 mini had several truncated, reasoning-only outputs on the all-nighter case, so the current evidence is incomplete rather than cleanly negative.

#### What did emerge

- `moralizing` was the most informative new axis in this round.
  - Both models could shift into an explicitly moralizing frame.
  - Both could also move toward a more plain task frame.
  - But DeepSeek more often retained residual normative language even under `ask_plain_task_frame`.
  - GPT-5 mini separated the two modes more cleanly.

#### Updated interpretation

This third round again argues against two overly broad readings:

- not every non-length high-level axis becomes hard to suppress;
- and not every explicit reversal request turns into a strong user-side controllability failure.

At the same time, it also weakens the idea that only pure length/scope directions matter.

The cleaner working picture is now:

- shallow format axes remain easy;
- some high-level axes remain broadly controllable (`clarify`, much of `sycophancy`, much of `contrarian`);
- the most credible residual-tendency axes are still those closest to a `too-much` assistant style:
  - `caveat/completeness`,
  - `next_step/proactivity`,
  - and, more weakly, the failure to fully drop a normative frame (`moralizing -> plain_task_frame`).

### 11.7 Fourth-round external benchmark: caveat, next-step, and moralizing cluster test

The next question was more specific:

- are `caveat`, `next_step`, and `moralizing` just three unrelated axes that each happen to show some residual tendency,
- or do they look more like a shared cluster of `too-much` assistant behavior?

To test that, the external benchmark was expanded again with a `v4` patch:

- `directional_control_research/data/external_multi_axis_controllability_v4_patch.json`
- merged runtime spec:
  - `resume/external_multi_axis_controllability_v4_merged.json`

and the benchmark was run on:

- `qwen` (local small instruct model)
- `deepseek_v4_flash`

with a fresh round of manual obedience-style annotation:

- `resume/external_multi_axis_obedience_annotations_v4_clusteraxes.jsonl`
- `resume/external_multi_axis_obedience_summary_v4_clusteraxes.md`

#### Why this `v4` patch was different

The purpose of `v4` was not simply to add more cases.
It was to add **overlap structure** across the three candidate axes.

Instead of giving each axis a fully separate case pool, the expanded set deliberately included:

- `caveat + next_step` overlap cases
- `moralizing + next_step` overlap cases
- `caveat + moralizing` overlap cases

The point of this design was:

- if all three negative modes fail only on totally separate case types, then they may be unrelated;
- but if the same kinds of cases repeatedly show residual `caveat`, residual `next_step`, and residual `moralizing` framing, then it becomes more plausible that they belong to a shared `too-much` cluster.

The final overlap structure was:

- `caveat` only: `3`
- `next_step` only: `6`
- `moralizing` only: `3`
- `caveat + next_step`: `7`
- `moralizing + next_step`: `3`
- `caveat + moralizing`: `2`

This matters because it makes later cluster-level interpretation less dependent on axis-specific case artifacts.

#### Why mean length was still checked first

As in the earlier external benchmark rounds, mean output length was used only as a **sanity check**:

- does the prompt actually separate the two modes at all;
- does the negative mode at least contract relative to the positive mode;
- is the benchmark alive enough to justify human-style obedience annotation.

Mean length was **not** treated as the final evidence for suppressibility failure.
Final interpretation came from text-level obedience labels.

#### First sanity-check pass

The `v4` benchmark did separate the modes in both models.

For `qwen`:

- `caveat`
  - `ask_more_complete_caveat`: mean `76.67`
  - `ask_no_extra_caveat`: mean `62.75`
- `next_step`
  - `ask_add_one_next_step`: mean `66.06`
  - `ask_no_next_step`: mean `25.88`
- `moralizing`
  - `ask_moralizing_frame`: mean `74.12`
  - `ask_plain_task_frame`: mean `54.12`

For `deepseek_v4_flash`:

- `caveat`
  - `ask_more_complete_caveat`: mean `96.75`
  - `ask_no_extra_caveat`: mean `50.33`
- `next_step`
  - `ask_add_one_next_step`: mean `112.5`
  - `ask_no_next_step`: mean `45.5`
- `moralizing`
  - `ask_moralizing_frame`: mean `72.0`
  - `ask_plain_task_frame`: mean `51.88`

These gaps were large enough to justify a second full annotation pass.

#### Annotation result

The formal `v4` annotation showed:

For `qwen`:

- `caveat`
  - `ask_more_complete_caveat`: `obey=12`
  - `ask_no_extra_caveat`: `obey=7, partial=4, disobey=1`
- `next_step`
  - `ask_add_one_next_step`: `obey=16`
  - `ask_no_next_step`: `obey=13, partial=3`
- `moralizing`
  - `ask_moralizing_frame`: `obey=5, partial=3`
  - `ask_plain_task_frame`: `obey=3, partial=5`

For `deepseek_v4_flash`:

- `caveat`
  - `ask_more_complete_caveat`: `obey=12`
  - `ask_no_extra_caveat`: `obey=8, partial=1, disobey=3`
- `next_step`
  - `ask_add_one_next_step`: `obey=16`
  - `ask_no_next_step`: `obey=7, partial=9`
- `moralizing`
  - `ask_moralizing_frame`: `obey=7, invalid=1`
  - `ask_plain_task_frame`: `obey=4, partial=4`

#### What this fourth round adds

This round sharpens the external picture in three ways.

First, it strengthens the claim that the observed controllability cost is **not** just a pure length phenomenon.

- `caveat` remains the strongest external residual-tendency axis;
- `next_step` remains the second strongest;
- `moralizing` shows a weaker but still nonzero residual pattern.

Second, it argues against the opposite extreme:

- not all high-level axes behave this way;
- the earlier `clarify`, `sycophancy`, and much of `contrarian` work remain much more controllable than this cluster.

Third, it supports a narrower cluster interpretation:

- the most persistent residual tendencies appear on directions that ask the assistant to do **one more thing**:
  - add one more caveat,
  - add one more next step,
  - add one more layer of normative framing.

This does **not** prove that all three axes share a single mechanism.
But it does support a more specific hypothesis than before:

**post-training controllability costs may concentrate in a cluster of `too-much` assistant directions, rather than in pure answer length alone or in all high-level axes uniformly.**

Among the three:

- `caveat/completeness` is the strongest member;
- `next_step/proactivity` is the second strongest;
- `moralizing -> plain_task_frame` is the weakest and most scenario-dependent member.

### 11.8 Aligned six-model comparison on the `v4` cluster benchmark

The `v4` cluster benchmark originally ran on:

- `qwen`
- `deepseek_v4_flash`

To determine whether the apparent cluster structure was robust or just a benchmark-version artifact, the next step was to align additional external models onto the **same three axes and the same `v4` case set**.

The intended aligned set was:

- `DeepSeek-7B-chat`
- `GPT-5 mini`
- `GPT-5.1`
- `Claude Sonnet 4.6`
- `qwen`
- `deepseek_v4_flash`

In practice:

- `GPT-5 mini` was successfully added via batch on the same `v4` benchmark;
- `GPT-5.1` was then added on the same `v4` benchmark;
- `Claude Sonnet 4.6` was added via a native Anthropic batch path;
- `qwen` and `deepseek_v4_flash` remained from the earlier `v4` pass;
- the local `DeepSeek-7B-chat` async runner remained unstable, but the same prompts were then completed via a synchronous fallback pass, producing a usable aligned fourth model.

Representative aligned summary:
- `resume/external_multi_axis_obedience_summary_v7_cluster_allmodels.md`

Representative aligned annotations:
- `resume/external_multi_axis_obedience_annotations_v6_aligned_clusteraxes.jsonl`
- `resume/external_multi_axis_gpt51_batch_v4_clusteraxes/external_multi_axis_gpt51_v4_negative_annotations.jsonl`
- `resume/external_multi_axis_claude_sonnet46_batch_v4_clusteraxes/external_multi_axis_claude_sonnet46_v4_negative_annotations.jsonl`

#### Aligned six-model counts

For `qwen`:

- `caveat`
  - `ask_more_complete_caveat`: `obey=12`
  - `ask_no_extra_caveat`: `obey=7, partial=4, disobey=1`
- `next_step`
  - `ask_add_one_next_step`: `obey=16`
  - `ask_no_next_step`: `obey=13, partial=3`
- `moralizing`
  - `ask_moralizing_frame`: `obey=5, partial=3`
  - `ask_plain_task_frame`: `obey=3, partial=5`

For `deepseek_v4_flash`:

- `caveat`
  - `ask_more_complete_caveat`: `obey=12`
  - `ask_no_extra_caveat`: `obey=8, partial=1, disobey=3`
- `next_step`
  - `ask_add_one_next_step`: `obey=16`
  - `ask_no_next_step`: `obey=7, partial=9`
- `moralizing`
  - `ask_moralizing_frame`: `obey=7, invalid=1`
  - `ask_plain_task_frame`: `obey=4, partial=4`

For `GPT-5 mini` on the same `v4` benchmark:

- `caveat`
  - `ask_more_complete_caveat`: `obey=8, invalid=4`
  - `ask_no_extra_caveat`: `obey=4, partial=6, disobey=2`
- `next_step`
  - `ask_add_one_next_step`: `obey=14, invalid=2`
  - `ask_no_next_step`: `obey=10, partial=5, invalid=1`
- `moralizing`
  - `ask_moralizing_frame`: `obey=8`
  - `ask_plain_task_frame`: `obey=2, partial=5, invalid=1`

For local `DeepSeek-7B-chat` on the same `v4` benchmark (sync fallback):

- `caveat`
  - `ask_more_complete_caveat`: `obey=12`
  - `ask_no_extra_caveat`: `obey=4, partial=1, disobey=7`
- `next_step`
  - `ask_add_one_next_step`: `obey=16`
  - `ask_no_next_step`: `obey=4, partial=5, disobey=7`
- `moralizing`
  - `ask_moralizing_frame`: `obey=8`
  - `ask_plain_task_frame`: `obey=0, partial=6, disobey=2`

For `GPT-5.1` on the same `v4` benchmark:

- `caveat`
  - `ask_no_extra_caveat`: `obey=10, partial=0, disobey=2`
- `next_step`
  - `ask_no_next_step`: `obey=14, partial=2, disobey=0`
- `moralizing`
  - `ask_plain_task_frame`: `obey=4, partial=4, disobey=0`

For `Claude Sonnet 4.6` on the same `v4` benchmark:

- `caveat`
  - `ask_no_extra_caveat`: `obey=9, partial=0, disobey=3`
- `next_step`
  - `ask_no_next_step`: `obey=13, partial=3, disobey=0`
- `moralizing`
  - `ask_plain_task_frame`: `obey=6, partial=2, disobey=0`

#### What the aligned comparison clarifies

The aligned comparison strengthens three points.

First, the cluster picture survives contact with additional strong models.

Even though `GPT-5 mini` is more controllable than `deepseek_v4_flash` on some earlier axes, the two newly added large models preserve the same broad ordering on this aligned `v4` benchmark:

- `caveat` remains the strongest residual-tendency axis;
- `next_step` remains the second strongest;
- `moralizing` remains weaker and more scenario-dependent.

Second, the ordering is not reducible to raw answer length alone.

The negative-mode failures are not only:
- getting longer,
- or failing to shorten.

They are more specifically:
- still adding caution,
- still adding one more procedural move,
- or still keeping one more layer of normative framing.

Third, the three models differ in degree rather than in kind.

- `qwen` retracts most cleanly on `next_step`
- `deepseek_v4_flash` leaves the strongest residual procedural push
- `GPT-5 mini` sits between them on `next_step`, but is notably sticky on `caveat`
- `GPT-5.1` is cleaner overall, but still leaves the same ordering
- `Claude Sonnet 4.6` is also cleaner overall, and again preserves the same ordering
- local `DeepSeek-7B-chat` is rougher overall, but in the same direction: it is hardest to retract on `caveat`, next hardest on `next_step`, and still leaves weaker residual `moralizing`

This makes the current external reading more specific:

**the most plausible external pattern is not a universal high-level controllability failure, and not a pure length-only failure, but a clustered residual bias toward doing one more assistant-like thing.**

The local `DeepSeek-7B-chat` result should not be over-read as a model-quality ranking, because it was obtained through a synchronous fallback path after the async endpoint proved unstable on the same prompts. But precisely because it is the roughest setting in the aligned set, its agreement on the ordering is still useful: it strengthens the cluster interpretation rather than weakening it. At this point the external benchmark no longer depends on a single provider or on small local models alone: the same cluster ordering now also appears in `GPT-5.1` and `Claude Sonnet 4.6`.

### 11.9 `v5` diagnostic follow-up for brittle `clarify` and `stance` directions

After the `v4` cluster benchmark, we added one narrower external diagnostic for two directions that had looked brittle in compact controlled-family induction:

- `clarify_first / answer_first`
- `deferential_uncertain / decisive_direct` (still evaluated under the existing `stance` axis)

This follow-up was diagnostic rather than expansionary. The question was:

- if these directions also looked sticky in stronger external models, then our compact-family failures might mainly reflect target-construction problems;
- if they remained broadly controllable externally, then their compact-family brittleness would more likely reflect weak native residual tendency rather than a missed major suppressibility cluster.

Representative summary:
- `resume/external_multi_axis_clarify_stance_summary_v5.md`

Execution status:

- `deepseek_v4_flash`: completed and readable
- `GPT-5 mini`: batch completed, but most rows were not reliably interpretable because reasoning tokens consumed the budget and left empty final answers
- local `qwen`: not usable for this run because the local endpoint first returned `502` and later refused connection entirely

#### DeepSeek v4 Flash reading

On `deepseek_v4_flash`, both axes were clearly prompt-responsive.

For `clarify`:

- `ask_clarify_first` usually did what it was supposed to do:
  - ask one key question first;
  - sometimes add a short provisional judgment after that question.
- `ask_answer_first` usually answered directly:
  - often with a bounded first move;
  - without reflexively drifting back into clarification-first behavior.

Examples:

- `task_deadline_blocker_001`
  - `ask_clarify_first`: asks whether the report is analytical, summary, or planning
  - `ask_answer_first`: directly says to open the document and start with title / cover information
- `clarify_room_search_001`
  - `ask_clarify_first`: asks for budget
  - `ask_answer_first`: simply says to set the budget first

Best reading:

- `clarify` is broadly controllable here;
- there is no strong evidence of a residual clarify-first bias pushing through the negative instruction.

For `stance`:

- `ask_hedged_cautious` usually became:
  - longer,
  - more conditional,
  - more uncertainty-aware,
  - more balanced.
- `ask_decisive_direct` usually became:
  - shorter,
  - more committed,
  - more one-sided,
  - more action-like.

Examples:

- `stance_offer_deadline_001`
  - hedged: discusses missing variables, risk tradeoffs, and delaying tactics
  - decisive: directly says to take today's offer
- `stance_exam_signup_001`
  - hedged: frames signup as low-cost option preservation with explicit uncertainty
  - decisive: directly says to sign up

There were still small imperfections:

- some `hedged` answers drifted into asking a clarifying question;
- one `ask_decisive_direct` row came back empty;
- some `decisive` answers still retained one warning line.

But overall the axis still looked much more like controllable prompt shaping than like a hard suppressibility-failure axis.

#### What `v5` adds

The `v5` diagnostic strengthens the interpretation of the earlier brittle family results:

- `clarify` and `stance` do **not** look like strong external sticky directions on current evidence;
- the earlier compact-family brittleness on those directions is therefore more likely to reflect weak native residual tendency than a missed major suppressibility cluster;
- this sharpens the contrast with the earlier external cluster:
  - `caveat / completeness`
  - `next_step / proactivity`
  - weaker `moralizing / plain_task_frame`

So the project now has cleaner negative evidence for two high-level directions that failed in compact family induction:

- they appear relatively controllable externally;
- they do not currently challenge the stronger `too-much assistant` cluster interpretation.

### 11.10 First controlled-family follow-up on `caveat`

The next step was to take the strongest new external axis, `caveat / completeness`, and push it into the same controlled-family training framework.

We built a `caveat_v1` family from the same `v4` caveat-native case manifold:
- `baseline`
- `more_complete_caveat`
- `no_extra_caveat`

Two first-pass stage-2 lines were trained:
- `baseline -> more_complete_caveat_stage2_v1`
- `baseline -> no_extra_caveat_stage2_v1`

Both lines trained cleanly, and both showed some axis movement under `caveat_controllability_matrix_v1`.

But the first family was not yet clean enough to retain.

Manual obedience-style annotation showed:
- `more_complete_caveat_stage2_v1`
  - `ask_more_complete_caveat`: `obey=6, partial=5, disobey=1`
  - `ask_no_extra_caveat`: `obey=7, partial=4, disobey=1`
- `no_extra_caveat_stage2_v1`
  - `ask_no_extra_caveat`: `obey=8, partial=4, disobey=0`
  - `ask_more_complete_caveat`: `obey=3, partial=4, disobey=5`

The pattern was asymmetrical in an unhelpful way:
- the suppressive side was cleaner;
- the positive side often drifted into more detail, more checklist structure, or generic explanation rather than a single brief caveat.

So `caveat_v1` was useful as diagnosis, but not yet a retained controlled-family result.

### 11.11 Cleaner rebuild on the positive caveat side

We then rebuilt only the positive side as `more_complete_caveat_stage2_v2`.

The key change was not a new case manifold or a new evaluation story. Instead, we narrowed the target:
- from a broad `more_complete_caveat` answer,
- to `baseline + exactly one short caveat`.

This change materially improved the result.

`caveat_v2` manual obedience annotation:
- `more_complete_caveat_stage2_v2`
  - `ask_more_complete_caveat`: `obey=7, partial=2, disobey=3`
  - `ask_no_extra_caveat`: `obey=9, partial=3, disobey=0`

Relative to `v1`, `v2` still does not look as clean as the retained `anti_underanswer` family. But it does show a more interpretable pattern:
- the negative side now has little template residue;
- the positive side more often adds one short caution point instead of spilling into broader checklist/helpfulness structure.

The current best reading is:
- `caveat` is now stronger than a mere external benchmark artifact;
- it can be partially isolated in a controlled family;
- but it is still not yet as clean, stable, or symmetric as the retained `anti_underanswer` line.

### 11.12 Caveat `v3`: targeted positive-side patch did not improve the family further

We also tried one narrower follow-up, `more_complete_caveat_stage2_v3`, which changed only three clearly failing `v2` positive-side cases:
- `troubleshoot_ram_blackscreen_001`
- `used_laptop_seller_001`
- `coworker_punch_in_001`

The goal was to test a very specific hypothesis:
- perhaps the remaining gap was concentrated in a few target-construction mistakes rather than in the family itself.

That hypothesis was not supported.

Manual obedience-style annotation for `v3`:
- `ask_more_complete_caveat`: `obey=6, partial=2, disobey=4`
- `ask_no_extra_caveat`: `obey=9, partial=3, disobey=0`

Compared with `v2`:
- the suppressive side stayed equally clean;
- the positive side did **not** improve;
- if anything, it became slightly worse.

This matters because it suggests that the remaining `caveat` problem is not just a tiny handful of bad target strings.

The current best reading of the `caveat` family is therefore:
- `v1`: clear signal, but heavily bundled;
- `v2`: materially cleaner and the best current version;
- `v3`: targeted patch did not push the line further.

So the family is now best treated as:
- **partial controlled-family evidence**
- but **not yet a second retained clean direction**

---

## 12. Final Mainline Interpretation

At the end of the retained mainline, the project?s best-supported interpretation is:

1. Base models contain a raw continuation tendency.
2. Baseline SFT regularizes that tendency into assistant behavior.
3. Different post-training directions reshape that assistant behavior differently.
4. Anti-underanswer is not simply longer by default; it is harder to suppress under explicit user-side boundary instructions.
5. This asymmetry is not well explained by:
   - a pure EOS failure,
   - a pure uncertainty-compensation story,
   - a pure local one-step continue preference,
   - or a pure wording-compression failure.
6. The retained evidence instead points to a mixed mechanism:
   - early planning/content-budgeting overshoot,
   - later continuation/stopping persistence,
   - embedded in a broader bundled assistant-policy bias.
7. Later anti-oriented SFT stages can strongly amplify this bias.
8. Preference-like stages can also push in the same direction, though current preference-stage evidence is weaker and non-monotonic.
9. The directional pattern survives a compact cross-family, cross-language replication.
10. The new external multi-axis work suggests that the cost is not confined to pure length/scope, but the first controlled-family extension beyond anti-underanswer is currently only partial: `caveat` can be isolated to a degree, but not yet at the same cleanliness level, and targeted `v3` patching did not further cleanly resolve the remaining gap.

---

## 13. What the Project Has Not Yet Cleanly Completed

The main missing pieces now are:

### 12.1 Quantitative planning-vs-stopping completion
This is no longer missing.

The focused `v2` annotation pack is complete and now supports a quantitative mixed-mechanism reading:
- `scope_minimal_sufficient` is relatively more planning-sensitive;
- `do_not_add_unasked_help` is strongly stopping-dominated.

What remains is not basic completion, but paper-quality presentation:
- compact tables,
- paired comparisons,
- and clear integration into the main results narrative.

### 12.2 Cross-over reversal control
No longer fully missing.
Current status:
- strong retained:
  - `anti_underanswer_sft_v5 -> preference_minimal` (`v2`)
- weaker partial:
  - `minimal_boundary_sft_v5 -> preference_baseline_task_primary_minanchor` (`v2`)
- not retained:
  - outward-from-minimal expansionary reversals

What is still missing now is not any reversal result at all, but:
- symmetric clean reversal evidence in both directions;
- and one more clean high-level direction beyond anti-underanswer.

### 12.3 Additional clean high-level direction contrast
Beyond `emoji_only`, the project still lacks a second clean high-level SFT direction that survives full evaluation.
That missing contrast matters because it would help determine whether hard suppressibility is:
- relatively specific to over-expansion / anti-underanswer,
- or a broader property of high-level SFT-stabilized assistant-policy biases.

### 12.4 Current local Qwen runtime issue

This diagnosis was narrowed substantially in the later 2026 rerun attempt.

What was checked:
- the previously written `qwen25_1p5b_baseline_sft_v5_phase2_oldprobe_smoke.jsonl` and `qwen25_1p5b_baseline_sft_v5_phase2_zh50_v1.jsonl` files contain genuinely bad `assistant_text` rows such as `!!!!"!!!#!!!$...`;
- the Chinese held-out source files themselves are not broken: when read through Python with UTF-8, the `heldout_eval_zh_*` cases decode normally;
- the `build_expanded_heldout_zh_50_v1.py` script constants also decode normally under Python, so the apparent PowerShell mojibake was a console-display artifact rather than proof of file corruption;
- rerunning the old one-case smoke probe with the current `eval_lora_adapter_phase2.py` path, same baseline adapter, same `heldout_eval_zh_smoke_1.json`, and CPU execution now produces a normal Chinese answer rather than punctuation garbage.

Current best reading:
- the local Qwen eval path is **not** globally broken;
- the old broken smoke / zh50 outputs should be treated as historical bad artifacts rather than as trusted evidence about the current runtime;
- the exact original failure trigger is still unresolved, because the punctuation-garbage behavior no longer reproduces on demand with the current script path.

The later device split clarified the remaining ambiguity:
- rerunning the same one-case Chinese sanity probe with `--device auto` **does** reproduce the old pathological punctuation-only output, and the new guard now aborts immediately on that path;
- rerunning the same case with `--device cpu` produces normal Chinese answers;
- so the current best diagnosis is not "Qwen is broken" but rather **"the default/auto device path is unsafe for this local setup, while the CPU path is usable."**

Practical fix applied:
- `eval_lora_adapter_phase2.py` now contains a pathological-output guard that aborts if generation matches the earlier punctuation-garbage pattern (for example `!!!!"!!!#...`) instead of silently writing bad rows to disk.

Operational implication:
- new Qwen reruns are unblocked in principle, but any fresh `zh50` run should be treated as a clean rerun rather than a continuation of the previously bad output files.
- until the local GPU/device-path issue is repaired, fresh Qwen-side evaluation should be run on **CPU only** if we need trustworthy outputs.

### 12.4a Clean Qwen `zh50` rerun on CPU

The `50`-item Chinese held-out pack was rerun cleanly on CPU only, without reusing the earlier bad `phase2_zh50_v1` file.

Assets:
- input pack: `directional_control_research/mechanism_experiment/outputs/heldout_eval_zh_50_v1.json`
- rerun shards and combined files: `tmp_qwen_zh50/`

Observed ordering on the clean CPU rerun:
- `avoid_underanswer`: baseline `23.44`, anti `33.78`, minimal `28.74`
- `scope_minimal_sufficient`: baseline `22.16`, anti `40.38`, minimal `27.28`
- `do_not_add_unasked_help`: baseline `24.10`, anti `28.64`, minimal `26.96`
- overall mean length across the three suppressive modes: baseline `23.23`, anti `33.45`, minimal `27.66`

Paired bootstrap deltas on the `50` aligned cases:
- `avoid_underanswer`, anti-minus-baseline: `+10.34` with 95% CI `[1.78, 19.84]`
- `scope_minimal_sufficient`, anti-minus-baseline: `+18.22` with 95% CI `[7.96, 31.68]`
- `do_not_add_unasked_help`, anti-minus-baseline: `+4.54` with 95% CI `[-0.48, 9.78]`

Reading:
- the clean rerun preserves the main family ordering;
- the strongest separation is again under `scope_minimal_sufficient`;
- a targeted long-tail rerun at `max_new_tokens=192` changed only two anti-side rows, but it increased the anti means in `avoid_underanswer` and `scope_minimal_sufficient`, so the original `96`-token summary was slightly conservative;
- the old punctuation-only `phase2_zh50_v1` file should therefore be treated as a bad historical artifact rather than as evidence about the phenomenon itself.

### 12.4aa Derived Qwen `zh50` forced-prefix continuation rerun

Because the clean `zh50` rerun widened the main held-out pack without widening forced-prefix, a derived `zh50` forced-prefix pack was built from the same `50` held-out cases.

Construction:
- input turns: `directional_control_research/mechanism_experiment/outputs/heldout_eval_zh_50_v1.json`
- forced prefix for each case: the `minimal_boundary` answer from `baseline_relational_instruction_scope_minimal_sufficient`
- derived pack asset: `tmp_qwen_zh50/forced_prefix_continuation_zh50_derived_v1.json`

Evaluation path:
- script: `directional_control_research/mechanism_experiment/scripts/eval_forced_prefix_continuation.py`
- device: CPU only
- modes: `neutral` and `scope_minimal_sufficient`
- output files:
  - `tmp_qwen_zh50/qwen25_1p5b_baseline_sft_v5_forced_prefix_zh50_derived_v1.json`
  - `tmp_qwen_zh50/qwen25_1p5b_anti_underanswer_sft_v5_forced_prefix_zh50_derived_v1.json`
  - `tmp_qwen_zh50/qwen25_1p5b_minimal_boundary_sft_v5_forced_prefix_zh50_derived_v1.json`

Observed continuation means (`100` aligned probe-mode rows per model):
- `baseline`: overall mean `0.00`; `neutral 0.00`; `scope_minimal_sufficient 0.00`
- `anti`: overall mean `1.94`; `neutral 2.12`; `scope_minimal_sufficient 1.76`
- `minimal`: overall mean `0.04`; `neutral 0.08`; `scope_minimal_sufficient 0.00`

Immediate-stop counts:
- `baseline`: `100/100`
- `anti`: `94/100`
- `minimal`: `99/100`

Paired anti-minus-baseline deltas on the aligned `probe_id × mode` rows:
- overall: `+1.94` with bootstrap 95% CI `[0.21, 4.33]`
- `neutral`: `+2.12` with bootstrap 95% CI `[0.02, 5.74]`
- `scope_minimal_sufficient`: `+1.76` with bootstrap 95% CI `[0.00, 4.90]`

Reading:
- the derived `zh50` forced-prefix pack still preserves the ordering `anti > minimal > baseline`;
- however, it is much harsher than the original retained `12`-probe forced-prefix suite, because the prefixes are taken from full `minimal_boundary` scope-min answers rather than from hand-built short prefixes;
- as a result, `baseline` and `minimal` almost always stop immediately, and the remaining signal is a small anti-side continuation tail rather than a broad three-row separation;
- this makes the derived `zh50` FP rerun a useful audit supplement, but not a substitute for the original retained forced-prefix evidence.

### 12.4ab Hand-built Qwen `zh50` forced-prefix continuation rerun

To reduce the over-strong stopping effect in the derived rerun, a second `zh50` forced-prefix pack was built manually with short minimum-sufficient prefixes written case-by-case.

Construction:
- input turns: `directional_control_research/mechanism_experiment/outputs/heldout_eval_zh_50_v1.json`
- hand-built prefix pack: `directional_control_research/mechanism_experiment/data/forced_prefix_continuation_zh50_handbuilt_v1.json`
- each row uses a short manually written prefix intended to answer the current request just enough while still leaving room for continuation

Evaluation path:
- script: `directional_control_research/mechanism_experiment/scripts/eval_forced_prefix_continuation.py`
- device: CPU only
- modes: `neutral` and `scope_minimal_sufficient`
- output files:
  - `tmp_qwen_zh50/qwen25_1p5b_baseline_sft_v5_forced_prefix_zh50_handbuilt_v1.json`
  - `tmp_qwen_zh50/qwen25_1p5b_anti_underanswer_sft_v5_forced_prefix_zh50_handbuilt_v1.json`
  - `tmp_qwen_zh50/qwen25_1p5b_minimal_boundary_sft_v5_forced_prefix_zh50_handbuilt_v1.json`

Observed continuation means (`100` aligned probe-mode rows per model):
- `baseline`: overall mean `2.54`; `neutral 2.26`; `scope_minimal_sufficient 2.82`
- `anti`: overall mean `4.08`; `neutral 2.12`; `scope_minimal_sufficient 6.04`
- `minimal`: overall mean `2.51`; `neutral 2.12`; `scope_minimal_sufficient 2.90`

Immediate-stop counts:
- `baseline`: `62/100`
- `anti`: `48/100`
- `minimal`: `63/100`

Paired deltas on aligned `probe_id × mode` rows:
- `anti-minus-baseline`, overall: `+1.54` with bootstrap 95% CI `[-0.01, 3.66]`
- `anti-minus-baseline`, `neutral`: `-0.14` with bootstrap 95% CI `[-1.48, 0.84]`
- `anti-minus-baseline`, `scope_minimal_sufficient`: `+3.22` with bootstrap 95% CI `[0.56, 7.28]`

Comparison with the derived rerun:
- the hand-built pack produces much less artificial hard-stop behavior from the prefix itself;
- unlike the derived rerun, the hand-built pack creates a clear separation specifically under `scope_minimal_sufficient`;
- the `neutral` side is flat, so the signal is narrower than in the original retained `12`-probe suite but more behaviorally interpretable than the derived rerun.

Reading:
- this hand-built `zh50` FP rerun is the better widened-FP supplement;
- it still does not reproduce the old retained FP effect size, but it does preserve the anti-side continuation signal in a cleaner way than the derived prefix construction;
- the safest summary is that widened Qwen FP evidence remains mode-concentrated: the continuation gap is clearest when the user explicitly reinforces minimal sufficiency.

### 12.4b Other previously suspicious model outputs

The same recheck pass was used to distinguish true model/runtime problems from historical artifacts and PowerShell display noise.

Qwen smoke files:
- several early non-CPU Qwen smoke files (`qwen25_1p5b_*_smoke_default.jsonl`, `qwen25_1p5b_*_smoke_phase2.jsonl`, and the old `phase2_oldprobe/zh50` files) contain the same punctuation-only pathology;
- the corresponding CPU smoke files are normal enough to read as genuine model outputs, not display artifacts.

So those early Qwen smoke failures are best read as the same unsafe-device-path problem, not as evidence that multiple Qwen variants inherently cannot produce normal outputs.

InternLM2 smoke:
- `internlm2_1p8b_baseline_sft_v1_smoke_default_cpu.jsonl` contains an empty first-row answer, so it remains suspicious;
- however, the adapter's recorded base path now points to a missing local model directory, and rerun attempts hit environment/base-path mismatches rather than reproducing a clean behavior failure;
- this means the old empty InternLM2 smoke should not currently be treated as claim-bearing evidence about model behavior. At the moment it is better classified as an unresolved environment-compatibility artifact.

Endpoint-side local Qwen:
- the older external-benchmark note about local `qwen` returning `502` and later refusing connections still reflects a real operational issue at the server layer;
- later port checks show `127.0.0.1:8083` is currently not accepting TCP connections.

So the endpoint failure and the punctuation-garbage generation failure should be kept separate:
- the former is a live local serving problem;
- the latter is a model-eval device-path problem with a working CPU fallback.

### 12.5 Best next deepening steps

The highest-yield next work from the current state is:

1. package the completed quantitative planning-vs-stopping decomposition cleanly;
2. stress-test the retained `anti -> preference_minimal` line with paired per-case reporting and bundled-generalization evaluation;
3. decide whether one more clean retained high-level SFT direction is still worth the remaining time after the negative `affect` and `stance` explorations;
4. extend the new external multi-axis benchmark with obedience-style annotation rather than relying only on first-pass structural reading and coarse rule checks.

---

## 14. Compressed Executive Summary

If the whole mainline is compressed into one paragraph:

The project began as a broad study of directional control and prompt-side assistant behavior, including prompt-taxonomy work and rough base-vs-chat comparisons. Those early explorations showed that high-level assistant directions are not cleanly one-dimensional and that post-training strongly reshapes behavior, but they did not yet isolate the sticky phenomenon. The work then shifted to a controlled Qwen SFT-family setup with `baseline`, `anti_underanswer`, and `minimal_boundary`, where it became clear that anti-underanswer is harder to suppress under explicit user-side boundary instructions. The rest of the project decomposed that asymmetry with EOS/tail supervision tests, uncertainty probes, compression-vs-pruning analysis, branchpoint scoring, forced-prefix continuation, asymmetric controllability, stage-split training, and bundled generalization. The retained evidence now supports a mixed mechanism picture: hard-to-suppress over-expansion is best understood as a bundled assistant-policy bias spanning both early planning/content-budgeting and later continuation/stopping, which can be further amplified by later post-training stages and directionally replicated in another open chat family.
