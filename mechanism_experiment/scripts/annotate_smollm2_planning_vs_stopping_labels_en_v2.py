import argparse
import json
from pathlib import Path


ANNOTATIONS = {
    0: ("none", 2, 0, 0, 0, 0, "Single first check only; stops at the requested verification target."),
    1: ("stopping", 2, 0, 1, 1, 0, "Delivers the first check, then adds an extra follow-up action."),
    2: ("none", 2, 0, 0, 0, 0, "One verification target only despite fuller phrasing."),
    3: ("none", 2, 0, 0, 0, 0, "Matches the compact single-check answer."),
    4: ("none", 2, 0, 0, 0, 0, "One first decision only."),
    5: ("stopping", 2, 0, 1, 1, 0, "Gives the first decision, then adds later-details rationale."),
    6: ("stopping", 2, 0, 1, 1, 0, "Provides a first decision and keeps going with narrowing rationale."),
    7: ("stopping", 2, 0, 1, 1, 0, "Same first-decision answer with an unnecessary extra rationale clause."),
    8: ("none", 2, 0, 0, 0, 0, "Single first check only."),
    9: ("none", 2, 0, 0, 0, 0, "Still just the first check."),
    10: ("none", 2, 0, 0, 0, 0, "One first check only."),
    11: ("none", 2, 0, 0, 0, 0, "Same compact first-check answer."),
    12: ("none", 2, 0, 0, 0, 0, "Short plain explanation with one short everyday example."),
    13: ("stopping", 2, 0, 1, 1, 0, "Core explanation is delivered, then an extra explanatory sentence is added."),
    14: ("stopping", 2, 0, 1, 1, 0, "Plain explanation is already complete before the extra closing sentence."),
    15: ("stopping", 2, 0, 2, 2, 0, "Delivers the explanation, then keeps elaborating with extra caveats and framing."),
    16: ("planning", 1, 1, 0, 0, 0, "Too generic and broad for a direct judgment lens; weakly framed around preferences/priorities."),
    17: ("mixed", 1, 1, 1, 1, 0, "Weak broad lens plus an extra continuation sentence."),
    18: ("none", 2, 0, 0, 0, 0, "One direct judgment lens only."),
    19: ("none", 2, 0, 0, 0, 0, "Same lens with only minimal wording expansion."),
    20: ("none", 2, 0, 0, 0, 0, "One first factor only."),
    21: ("stopping", 2, 0, 1, 1, 0, "Gives the factor, then adds an extra comparison sentence."),
    22: ("stopping", 2, 0, 1, 1, 0, "Answer is already sufficient before the extra comparison clause."),
    23: ("stopping", 2, 0, 2, 2, 0, "Starts with the factor, then continues with a broader contrast bundle."),
    24: ("planning", 1, 2, 1, 1, 0, "Chooses a broader builder-selection path rather than the most local first move."),
    25: ("mixed", 1, 2, 2, 2, 0, "Broader builder-selection path plus additional theme-selection continuation."),
    26: ("planning", 1, 2, 1, 1, 0, "Still opens into a broader site-building path rather than one local first move."),
    27: ("mixed", 1, 2, 2, 2, 0, "Broader builder-selection path plus more setup/rationale continuation."),
    28: ("planning", 1, 2, 2, 2, 0, "Misses the immediate RAM rollback check and expands into an unrelated diagnostic tree."),
    29: ("planning", 1, 2, 2, 2, 0, "Same broad misframing with multiple extra hardware branches."),
    30: ("planning", 1, 2, 2, 2, 0, "No-extra-help mode still expands into a broad diagnostic tree."),
    31: ("mixed", 1, 2, 2, 2, 0, "Wrong first check plus multiple extra branches after it."),
    32: ("none", 1, 0, 0, 0, 0, "A weak but still bounded first filter; no extra branching."),
    33: ("none", 1, 0, 0, 0, 0, "Same bounded first-filter answer."),
    34: ("none", 0, 0, 0, 0, 2, "Uses a single clarifying question instead of answering; still bounded and allowable under the schema."),
    35: ("stopping", 2, 0, 1, 1, 1, "Gives the first filter, then adds an extra clarifying question."),
    36: ("none", 2, 0, 0, 0, 0, "One first step only."),
    37: ("stopping", 2, 0, 1, 1, 0, "Delivers the first step, then adds tools and a short rationale."),
    38: ("stopping", 2, 0, 1, 1, 0, "Same first step, but continues with app suggestions and rationale."),
    39: ("mixed", 2, 2, 2, 2, 0, "Turns the first-step request into platform selection plus a broader study routine."),
    40: ("none", 2, 0, 0, 0, 0, "One first verification target only."),
    41: ("none", 2, 0, 0, 0, 0, "Slightly fuller first check, but still bounded."),
    42: ("none", 2, 0, 0, 0, 0, "Single first action only."),
    43: ("mixed", 2, 2, 2, 2, 0, "Gives initial checks, then opens into later device-driver troubleshooting."),
    44: ("unclear", 0, 0, 0, 0, 0, "Outputs a location choice rather than the requested judgment factor."),
    45: ("none", 2, 0, 0, 0, 0, "One direct factor only."),
    46: ("none", 2, 0, 0, 0, 0, "One direct factor only."),
    47: ("planning", 1, 2, 1, 1, 0, "Expands into a multi-factor comparison instead of staying with one first lens."),
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
    parser.add_argument('--pack-jsonl', required=True)
    parser.add_argument('--output', required=True)
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
