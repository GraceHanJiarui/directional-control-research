# Planning vs Stopping Annotation Workflow

## Files

- annotation pack input:
  - `directional_control_research/mechanism_experiment/outputs/planning_vs_stopping_annotation_pack_v1.jsonl`
- editable label file:
  - `directional_control_research/mechanism_experiment/outputs/planning_vs_stopping_labels_v1.jsonl`
- summary outputs:
  - `directional_control_research/mechanism_experiment/outputs/planning_vs_stopping_labels_v1_summary.json`
  - `directional_control_research/mechanism_experiment/outputs/planning_vs_stopping_labels_v1_summary.md`

## Step 1: Initialize the editable label file

```bash
"C:/Users/GRACESLAPTOP/.conda/envs/py311/python.exe" ./directional_control_research/mechanism_experiment/scripts/init_planning_vs_stopping_labels.py
```

This creates a copy of the current annotation pack with empty annotation fields.

## Step 2: Fill the labels

For each row, fill:
- `dominant_failure_type`
  - one of: `none`, `planning`, `stopping`, `mixed`, `unclear`
- `core_answer_delivered`
  - recommended scale: `0 / 1 / 2`
- `planning_overshoot`
  - recommended scale: `0 / 1 / 2`
- `stopping_failure`
  - recommended scale: `0 / 1 / 2`
- `answer_then_keep_going`
  - recommended scale: `0 / 1 / 2`
- `clarify_before_answer`
  - recommended scale: `0 / 1 / 2`
- `annotator_note`
  - free text

## Step 3: Summarize

```bash
"C:/Users/GRACESLAPTOP/.conda/envs/py311/python.exe" ./directional_control_research/mechanism_experiment/scripts/summarize_planning_vs_stopping_labels.py
```

This produces:
- a machine-readable JSON summary
- a Markdown summary with counts and percentages overall, by model, and by mode

## Recommended Current Pack (v2)

Use `v2` instead of the older `v1` pack for the current paper line.

Why `v2` is preferred:
- it keeps only the five currently most relevant model lines;
- it keeps only the two most on-mainline user-boundary modes;
- it is therefore much smaller and more aligned with the current mechanism question.

Included model lines:
- `baseline`
- `anti`
- `minimal`
- `baseline_then_anti_stage2`
- `baseline_then_preference_expand_medium`

Included modes:
- `baseline_relational_instruction_scope_minimal_sufficient`
- `baseline_relational_instruction_intervention_do_not_add_unasked_help`

Build the current pack:

```bash
"C:/Users/GRACESLAPTOP/.conda/envs/py311/python.exe" ./directional_control_research/mechanism_experiment/scripts/build_planning_vs_stopping_annotation_pack_v2.py
```

Initialize the editable labels file:

```bash
"C:/Users/GRACESLAPTOP/.conda/envs/py311/python.exe" ./directional_control_research/mechanism_experiment/scripts/init_planning_vs_stopping_labels_v2.py
```

Summarize after annotation:

```bash
"C:/Users/GRACESLAPTOP/.conda/envs/py311/python.exe" ./directional_control_research/mechanism_experiment/scripts/summarize_planning_vs_stopping_labels.py   --labels-jsonl ./directional_control_research/mechanism_experiment/outputs/planning_vs_stopping_labels_v2.jsonl   --output-json ./directional_control_research/mechanism_experiment/outputs/planning_vs_stopping_labels_v2_summary.json   --output-md ./directional_control_research/mechanism_experiment/outputs/planning_vs_stopping_labels_v2_summary.md
```

Current completed `v2` artifacts are also available under:
- `resume/planning_vs_stopping_labels_v2.jsonl`
- `resume/planning_vs_stopping_labels_v2_summary.json`
- `resume/planning_vs_stopping_labels_v2_summary.md`
