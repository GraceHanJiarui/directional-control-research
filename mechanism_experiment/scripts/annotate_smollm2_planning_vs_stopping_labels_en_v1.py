import argparse
import json
from pathlib import Path


ANNOTATIONS = {
    0: ("none", 2, 0, 0, 0, 0, "Single first check; no clear overshoot."),
    1: ("none", 2, 0, 0, 0, 0, "Still stays on the first check despite a small conditional phrase."),
    2: ("none", 2, 0, 0, 0, 0, "One first verification target; no extra branch."),
    3: ("none", 2, 0, 0, 0, 0, "Same as baseline here; still one first verification target."),
    4: ("none", 2, 0, 0, 0, 0, "Short plain explanation with one everyday example."),
    5: ("mixed", 2, 2, 2, 2, 0, "Starts with a plain explanation, then opens into causes and a broader mini-lesson."),
    6: ("none", 2, 0, 0, 0, 0, "Still within a compact plain-explanation frame."),
    7: ("stopping", 2, 0, 1, 1, 0, "Core explanation is delivered, then an extra elaborating clause is added."),
    8: ("none", 2, 0, 0, 0, 0, "One direct judgment lens only."),
    9: ("stopping", 2, 0, 1, 1, 0, "Gives the lens, then adds an extra aligning sentence."),
    10: ("none", 2, 0, 0, 0, 0, "One direct factor; no extra help."),
    11: ("none", 2, 0, 0, 0, 0, "Still one direct factor despite slightly fuller phrasing."),
    12: ("planning", 1, 2, 1, 1, 0, "Chooses weak first checks and expands into a broader diagnostic branch."),
    13: ("planning", 1, 2, 1, 1, 0, "Same broad misframing; first checks are poorly targeted and open a wider branch."),
    14: ("planning", 1, 2, 1, 1, 0, "No-extra-help mode still expands into a broader diagnostic tree."),
    15: ("mixed", 1, 2, 2, 2, 0, "Weak initial framing plus extra later hardware branches."),
    16: ("none", 2, 0, 0, 0, 0, "One first filter only."),
    17: ("none", 2, 0, 0, 0, 0, "Matches the compact first-filter answer."),
    18: ("none", 0, 0, 0, 0, 2, "Uses one key clarifying question, which is allowed here."),
    19: ("stopping", 2, 0, 1, 1, 1, "Gives the first filter, then adds an extra clarification question."),
    20: ("none", 2, 0, 0, 0, 0, "One first step only."),
    21: ("stopping", 2, 0, 1, 1, 0, "Gives the first step, then adds tool examples and rationale."),
    22: ("stopping", 2, 0, 1, 1, 0, "Delivers the first step, then keeps going with app suggestions."),
    23: ("mixed", 2, 2, 2, 2, 0, "Turns a first-step request into a broader platform-selection and study routine."),
}


def load_jsonl(path: str):
    rows = []
    with Path(path).open('r', encoding='utf-8-sig') as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--pack-jsonl', default='resume/planning_vs_stopping_smollm2_en_pack_v1.jsonl')
    parser.add_argument('--output', default='resume/planning_vs_stopping_smollm2_en_labels_v1.jsonl')
    args = parser.parse_args()

    rows = load_jsonl(args.pack_jsonl)
    if len(rows) != len(ANNOTATIONS):
        raise ValueError(f'Expected {len(ANNOTATIONS)} rows, found {len(rows)}')

    out_rows = []
    for i, row in enumerate(rows):
        label, core, planning, stopping, keep_going, clarify, note = ANNOTATIONS[i]
        row['dominant_failure_type'] = label
        row['core_answer_delivered'] = core
        row['planning_overshoot'] = planning
        row['stopping_failure'] = stopping
        row['answer_then_keep_going'] = keep_going
        row['clarify_before_answer'] = clarify
        row['annotator_note'] = note
        out_rows.append(row)

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open('w', encoding='utf-8', newline='\n') as f:
        for row in out_rows:
            f.write(json.dumps(row, ensure_ascii=False) + '\n')
    print(f'wrote {len(out_rows)} labels to {out_path}')


if __name__ == '__main__':
    main()
