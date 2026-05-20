# Planning vs Stopping Annotation Schema

This schema separates two failure modes in directional-control outputs:
- `planning_overshoot`: the model expands the task structure too early;
- `stopping_failure`: the model reaches a minimally sufficient answer and then keeps going.

## Unit
Annotate one response at a time.

Required identifiers:
- `case_id`
- `experiment_mode`
- `actor_stage`
- `user_text`
- `assistant_text`

## Core fields

### `core_answer_delivered`
Scale: `0 / 1 / 2`
- `0`: the response does not deliver the requested first-step/core answer
- `1`: partial or weak core answer
- `2`: clearly delivers the requested core answer

### `planning_overshoot`
Scale: `0 / 1 / 2`
- `0`: does not expand the task structure beyond the requested boundary
- `1`: some extra structuring or steering
- `2`: clearly expands into a larger plan / diagnostic tree / multi-step framework

### `stopping_failure`
Scale: `0 / 1 / 2`
- `0`: stops close to the minimum sufficient point
- `1`: mild continuation after the core answer
- `2`: clearly keeps going after the core answer has already been delivered

### `answer_then_keep_going`
Scale: `0 / 1 / 2`
- `0`: no
- `1`: somewhat
- `2`: yes, the core answer appears first and the rest is mostly unnecessary continuation

### `clarify_before_answer`
Scale: `0 / 1 / 2`
- `0`: no unnecessary clarification before answering
- `1`: mild or arguably useful clarification before answering
- `2`: clearly postpones the answer in favor of clarification

### `dominant_failure_type`
Recommended values:
- `none`: no meaningful failure under this rubric
- `planning`: early task expansion / wrong discourse path
- `stopping`: unnecessary continuation after the core answer
- `mixed`: both are clearly present
- `unclear`: malformed, too weak, or too off-target to assign cleanly

## Fast heuristic
1. Ask whether the core answer appears at all.
2. If not, the main issue is more likely `planning_overshoot` or `clarify_before_answer` than `stopping_failure`.
3. If yes, ask whether the response could have stopped right there.
4. If the answer is yes but it continued, score `stopping_failure` higher.
