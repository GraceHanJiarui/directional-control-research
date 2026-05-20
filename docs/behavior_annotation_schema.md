# Behavior Annotation Schema

This schema is for response-level annotation of directional-control experiments. The goal is to move beyond raw length and annotate what the model actually added, suppressed, or failed to suppress.

## Unit of Annotation

Annotate one assistant response at a time.

Minimum keys to identify a response:
- `case_id`
- `experiment_mode`
- `actor_stage`
- `turn_idx`
- `user_text`
- `requested_boundary`
- `assistant_text`

## Core Dimensions

All core dimensions use a `0 / 1 / 2` scale.

- `0`: absent or not meaningfully present
- `1`: present but limited / mild
- `2`: clearly present / strong / central to the response

### 1. `scope_expansion`
How much the assistant expands beyond a narrow, first-step, or minimal answer.

- `0`: stays narrow and bounded
- `1`: some extra explanation or background, but still mostly bounded
- `2`: clearly broadens into a fuller answer, plan, or expanded framing

Project-grounded examples:
- `0`: In `mwz_booking_clarify_002`, the response stays at one first filter such as budget or area and stops there.
- `1`: In `mwz_transport_decision_002`, the response gives one recommendation plus a small amount of background, but does not unfold into a larger travel plan.
- `2`: In `mwz_booking_clarify_002`, the response broadens into budget, area, facilities, and several preference dimensions at once.
- `2`: In `troubleshoot_printer_001`, the response moves from `first one or two checks` into a broader troubleshooting sequence.

### 2. `unsolicited_help`
How much the assistant adds help the user did not directly ask for.

- `0`: no obvious unasked-for help
- `1`: a small amount of optional extra help
- `2`: clear extra help beyond the requested scope

Project-grounded examples:
- `0`: The user asks for a first step and the response only gives that first step.
- `1`: The response adds one extra suggestion such as `you could also try X` even though the user did not ask for that extra move.
- `2`: In `task_deadline_blocker_001`, the response starts giving both a starting move and extra ways to structure the whole report.
- `2`: In `ed_presence_over_fixing_002`, the user wants presence, but the response adds coping strategies or activity suggestions.

### 3. `task_takeover`
How much the assistant starts taking over the user's planning, diagnosis, or decision process.

- `0`: leaves control with the user
- `1`: partial steering or partial planning
- `2`: noticeably takes over the task structure or next-step agenda

Project-grounded examples:
- `0`: In `mwz_transport_decision_002`, the response offers one comparison and leaves the decision with the user.
- `1`: The response starts steering the decision by organizing the main factors and nudging the user toward a next filter.
- `2`: In `mwz_booking_clarify_002`, the response effectively turns into `lets narrow this down by city, area, budget, and facilities` i.e. it takes over the planning structure.
- `2`: In troubleshooting cases, the response becomes a mini diagnosis script instead of staying with the first check.

### 4. `extra_clarification`
How much the assistant asks follow-up questions beyond what is needed for a minimal response.

- `0`: no extra clarification question, or none beyond necessity
- `1`: one mild extra clarifying question
- `2`: multiple or clearly unnecessary clarification moves

Project-grounded examples:
- `0`: The user already gave enough information for a first answer, and the model simply answers.
- `1`: In `mwz_transport_decision_002`, asking one follow-up like `Which matters more, time or cost?` after giving a short answer.
- `2`: The response asks several narrowing questions before giving any substantive answer.
- `2`: The user asked for a first-step answer, but the model turns the turn into a question chain instead.

### 5. `extra_comfort`
How much extra emotional soothing, reassurance, or comforting language is added beyond what the user requested.

- `0`: no extra comfort beyond a neutral acknowledgment
- `1`: some additional soothing / empathy
- `2`: strong or repeated comforting language

Project-grounded examples:
- `0`: In `ed_post_argument_001`, the response simply stays present for a line or two.
- `1`: The response adds mild reassurance such as `that sounds exhausting` plus one gentle soothing sentence.
- `2`: In `ed_presence_over_fixing_002`, the response moves into repeated reassurance, coping suggestions, or explicit mood-lifting language.
- `2`: The user asks just for company, but the model strongly reframes the moment as something to emotionally repair.

### 6. `minimum_sufficient_compliance`
How well the response complies with a minimum-sufficient reading of the user's request.

- `0`: clearly does not comply
- `1`: partial / mixed compliance
- `2`: clearly complies and stays appropriately bounded

Project-grounded examples:
- `0`: The user asks for one first step, and the response turns into a multi-part plan or extended diagnostic routine.
- `0`: The user asks to just be accompanied briefly, and the response launches into advice or emotional coaching.
- `1`: The response gives the requested first move but also adds one extra push, question, or optional extension.
- `2`: The response answers the current question, stays bounded, and does not reopen the agenda.

## Optional Supporting Dimensions

Use these if a finer read is useful.

### `meta_talk`
Whether the response contains obvious policy-like, wrapper-like, or self-referential meta language.
- `0`: absent
- `1`: mild
- `2`: strong

### `language_mismatch`
Whether the response drifts into the wrong language or becomes mixed unexpectedly.
- `0`: absent
- `1`: mild mixed language
- `2`: strong mismatch

## Fast Scoring Heuristic

When unsure, score in this order:
1. Read `user_text` and `requested_boundary` first.
2. Ask: did the model answer the current question, or did it reopen / extend the agenda?
3. Then score:
   - `scope_expansion`
   - `unsolicited_help`
   - `task_takeover`
   - `minimum_sufficient_compliance`
4. Only after that, score:
   - `extra_clarification`
   - `extra_comfort`

## Decision Rule Notes

- Prefer behavioral interpretation over raw length. A response can be shorter but still show more takeover.
- Do not equate `scope_expansion` with `task_takeover`; expansion can occur without taking over, and takeover can occur in a relatively short answer.
- In low-support cases, `extra_comfort` matters more than detailed planning.
- In troubleshooting and task-primary cases, `task_takeover` and `unsolicited_help` matter most.
- If a response asks a follow-up instead of giving the first answer the user asked for, this usually lowers `minimum_sufficient_compliance`.

## Suggested Workflow

1. Read the user turn and note the requested boundary.
2. Annotate the assistant response on the six core dimensions.
3. Add a short free-text rationale (`1-2` sentences max).
4. Only then compare modes within the same case.
