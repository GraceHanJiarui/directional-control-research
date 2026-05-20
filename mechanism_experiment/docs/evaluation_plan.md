# First-Pass Evaluation Plan

Evaluate the three trained adapters on the existing directional-control evaluation splits.

## Minimal first pass
Use the Chinese 24-case set already assembled in the main project.

Recommended annotation fields:
- `boundary_following` in {0,1,2}
- `answer_before_redirect` in {0,1,2}
- `override_type` in {none, clarification, planning, comfort, takeover, continuation}
- `override_severity` in {0,1,2}

## Minimal success pattern
- `anti_underanswer_sft`:
  - lower `boundary_following`
  - lower `answer_before_redirect`
  - more `clarification` / `planning` / `takeover`
- `minimal_boundary_sft`:
  - higher `boundary_following`
  - higher `answer_before_redirect`
  - fewer override labels
