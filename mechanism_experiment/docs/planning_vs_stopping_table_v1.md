# Planning vs Stopping Table v1

This table is a first structured reading pass over the current `1.5B CPU userboundary_v2` outputs.
It is not yet a full human-labeled annotation study, but it records the current best reading of the dominant failure type in several representative cases.

| case_id | representative anti behavior | dominant failure type | why |
|---|---|---|---|
| `clarify_study_restart_001` | asks about the user's goal before giving the requested first step | planning overshoot / clarify-before-answer | the model reopens the agenda before satisfying the narrow request |
| `clarify_room_search_001` | turns a first-step request into a 3-step plan under `scope_minimal_sufficient` | planning overshoot | the answer expands the plan structure before the user asked for it |
| `dd_everyday_choice_002` | gives a core factor, then continues with extra comparison and recommendation detail | stopping failure | the minimally sufficient answer is reached, but the model keeps elaborating |
| `mwz_concept_explain_001` | after a short explanation, continues with examples and extra background | mixed, leaning stopping failure | the core concept is already answered, then extra illustration gets added |
| `troubleshoot_ram_blackscreen_001` | often provides multiple checks even when asked for the first one or two only | mixed | some runs look like over-budgeted troubleshooting plans, others like not stopping after the first check |
| `troubleshoot_phone_storage_001` | tends to give a broader cleanup path instead of only the highest-priority first check | mixed, leaning planning overshoot | the model allocates a larger action budget than requested |

## Current summary

The current mechanism picture should not be reduced to a single late-stop account.
At least two failure modes are already visible:
- **planning overshoot**: the model chooses too large a discourse plan before answering the narrow user request
- **stopping failure**: the model reaches a minimally sufficient answer, then keeps adding extra material

This table is meant to support the next step: turning the current qualitative reading into a more explicit case-level annotation pass.
