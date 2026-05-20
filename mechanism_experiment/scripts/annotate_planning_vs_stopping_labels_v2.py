import argparse
import json
from pathlib import Path


ANNOTATIONS = {
    0: ("planning", 0, 2, 0, 0, 0, "Locks onto the earlier everyday-choice thread instead of the RAM question."),
    1: ("planning", 0, 1, 0, 0, 0, "Sets up an answer but never actually answers the RAM question."),
    2: ("unclear", 0, 0, 0, 0, 0, "Generic filler; no core answer."),
    3: ("planning", 2, 2, 0, 0, 0, "Immediately expands into a repair tree with poor first checks."),
    4: ("planning", 0, 2, 0, 0, 0, "Completely rewrites to the earlier time-management thread."),
    5: ("unclear", 0, 0, 0, 0, 0, "Sets up an answer but provides no actionable content."),
    6: ("stopping", 2, 0, 2, 2, 0, "Gives a core check list then adds unnecessary third check."),
    7: ("unclear", 0, 0, 0, 0, 0, "No substantive answer."),
    8: ("planning", 2, 2, 0, 0, 0, "Broad fault-cause framing rather than one or two first checks."),
    9: ("mixed", 2, 2, 2, 2, 0, "Turns into a full procedure/manual."),
    10: ("none", 2, 0, 0, 0, 0, "One direct first filter."),
    11: ("none", 2, 0, 0, 0, 0, "Compact first-step answer."),
    12: ("none", 2, 0, 0, 0, 0, "Compact first-step answer."),
    13: ("planning", 2, 2, 1, 1, 0, "Expands the first step into a broader search strategy."),
    14: ("none", 2, 0, 0, 0, 0, "Compact first-step answer."),
    15: ("none", 2, 0, 0, 0, 0, "Compact first-step answer."),
    16: ("none", 2, 0, 0, 0, 0, "Compact first-step answer."),
    17: ("unclear", 1, 0, 0, 0, 1, "Turns the requested first step into a clarification question."),
    18: ("mixed", 2, 2, 2, 2, 0, "First step plus extra budgeting/time framework and extra steering."),
    19: ("none", 2, 0, 0, 0, 0, "Compact first-step answer."),
    20: ("none", 2, 0, 0, 0, 0, "Compact first-step answer."),
    21: ("mixed", 2, 2, 2, 2, 0, "Immediately unfolds a multi-step study plan."),
    22: ("none", 2, 0, 0, 0, 0, "Compact first-step answer."),
    23: ("planning", 2, 1, 0, 0, 0, "Commits too early to a concrete path instead of a simple restart step."),
    24: ("none", 2, 0, 0, 0, 0, "Compact first-step answer."),
    25: ("none", 2, 0, 0, 0, 0, "Compact first-step answer."),
    26: ("mixed", 2, 2, 2, 2, 0, "Turns into a multi-step study routine."),
    27: ("mixed", 2, 2, 2, 2, 0, "Clear multi-step plan after the first step."),
    28: ("none", 2, 0, 0, 0, 0, "One clean first step."),
    29: ("unclear", 0, 0, 0, 0, 0, "Acknowledges but does not answer."),
    30: ("none", 2, 0, 0, 0, 0, "One criterion only."),
    31: ("none", 2, 0, 0, 0, 0, "One criterion only."),
    32: ("none", 2, 0, 0, 0, 0, "One criterion only."),
    33: ("none", 2, 0, 0, 0, 0, "A bit chatty but still basically one criterion."),
    34: ("none", 2, 0, 0, 0, 0, "Still one compact criterion cluster."),
    35: ("none", 2, 0, 0, 0, 0, "Slightly richer wording but still near-minimal."),
    36: ("none", 2, 0, 0, 0, 0, "Compact first criterion."),
    37: ("none", 2, 0, 0, 0, 0, "Compact first criterion."),
    38: ("stopping", 2, 0, 1, 1, 0, "Answers, then adds unnecessary discussion about both options."),
    39: ("none", 2, 0, 0, 0, 0, "Compact first criterion."),
    40: ("unclear", 0, 0, 0, 0, 0, "Just mirrors the user; no answer."),
    41: ("unclear", 0, 0, 0, 0, 0, "Just mirrors the user; no answer."),
    42: ("unclear", 0, 0, 0, 0, 0, "Just mirrors the user; no answer."),
    43: ("stopping", 2, 0, 2, 2, 0, "Valid affective acknowledgment, then a full advice bundle."),
    44: ("stopping", 2, 0, 2, 2, 0, "Acknowledges then keeps going with extra reframing/advice."),
    45: ("none", 2, 0, 0, 0, 0, "Short acknowledgment only."),
    46: ("stopping", 2, 0, 2, 2, 0, "Adds extra coping advice after acknowledgment."),
    47: ("stopping", 2, 0, 2, 2, 0, "Adds unnecessary coping advice after acknowledgment."),
    48: ("stopping", 2, 0, 2, 2, 0, "Adds multiple extra coping suggestions."),
    49: ("unclear", 0, 0, 0, 0, 0, "Self-focused mirror rather than answer."),
    50: ("none", 2, 0, 0, 0, 0, "Minimal acknowledgment fits the request."),
    51: ("none", 2, 0, 0, 0, 0, "Minimal acknowledgment fits the request."),
    52: ("none", 2, 0, 0, 0, 0, "Minimal acknowledgment fits the request."),
    53: ("planning", 1, 1, 0, 0, 2, "Defers into a new conversation branch/question."),
    54: ("unclear", 1, 0, 0, 0, 1, "Reframes the user's wording instead of clearly answering."),
    55: ("none", 2, 0, 0, 0, 0, "Short acknowledgment only."),
    56: ("none", 2, 0, 0, 0, 0, "Short acknowledgment only."),
    57: ("none", 2, 0, 0, 0, 0, "Short acknowledgment only."),
    58: ("stopping", 2, 0, 1, 1, 0, "Answers and then adds extra meta-closure."),
    59: ("unclear", 1, 0, 0, 0, 1, "Reframes instead of directly answering."),
    60: ("none", 2, 0, 0, 0, 0, "Two first checks, still within spec."),
    61: ("none", 2, 0, 0, 0, 0, "Two first checks, still within spec."),
    62: ("none", 2, 0, 0, 0, 0, "One first check only."),
    63: ("mixed", 2, 1, 2, 2, 0, "Starts with first checks, then adds replacement and later escalation."),
    64: ("none", 2, 0, 0, 0, 0, "Compact first verification target."),
    65: ("stopping", 2, 0, 2, 2, 0, "Three checks after a one-check request."),
    66: ("stopping", 2, 0, 2, 2, 0, "Three checks after a one-check request."),
    67: ("stopping", 2, 0, 2, 2, 0, "Three checks after a one-check request."),
    68: ("mixed", 2, 1, 2, 2, 0, "Three-step troubleshooting plus escalation clause."),
    69: ("unclear", 0, 0, 0, 0, 0, "Restates the problem instead of answering."),
    70: ("stopping", 2, 0, 2, 2, 0, "Adds three checks and extra hardware branches."),
    71: ("stopping", 2, 1, 2, 2, 0, "Three checks, including weakly related ones."),
    72: ("none", 2, 0, 0, 0, 0, "Two first checks only."),
    73: ("mixed", 2, 1, 2, 2, 0, "Starts with the right first check, then unfolds more diagnostics."),
    74: ("stopping", 2, 0, 2, 2, 0, "Three checks after a one-or-two-check request."),
    75: ("stopping", 2, 0, 2, 2, 0, "Three checks after a one-or-two-check request."),
    76: ("stopping", 2, 0, 2, 2, 0, "Three checks after a one-or-two-check request."),
    77: ("stopping", 2, 0, 2, 2, 0, "Three checks after a one-or-two-check request."),
    78: ("stopping", 2, 0, 2, 2, 0, "Three checks plus an extra escalation clause."),
    79: ("stopping", 2, 0, 2, 2, 0, "Three checks after a one-or-two-check request."),
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input-jsonl",
        default="directional_control_research/mechanism_experiment/outputs/planning_vs_stopping_annotation_pack_v2.jsonl",
    )
    parser.add_argument(
        "--output-jsonl",
        default="directional_control_research/mechanism_experiment/outputs/planning_vs_stopping_labels_v2.jsonl",
    )
    args = parser.parse_args()

    in_path = Path(args.input_jsonl)
    out_path = Path(args.output_jsonl)
    rows = []
    with in_path.open("r", encoding="utf-8-sig") as f:
        for i, line in enumerate(f):
            row = json.loads(line)
            if i not in ANNOTATIONS:
                raise KeyError(f"missing annotation for row {i}")
            label, core, planning, stopping, keep_going, clarify, note = ANNOTATIONS[i]
            row["dominant_failure_type"] = label
            row["core_answer_delivered"] = core
            row["planning_overshoot"] = planning
            row["stopping_failure"] = stopping
            row["answer_then_keep_going"] = keep_going
            row["clarify_before_answer"] = clarify
            row["annotator_note"] = note
            rows.append(row)
    out_path.write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(f"wrote {len(rows)} rows to {out_path}")


if __name__ == "__main__":
    main()
