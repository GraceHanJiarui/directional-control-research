import argparse
import json
from pathlib import Path


SYSTEM_PROMPTS = {
    "baseline_sft": "You are a helpful assistant. Answer the user directly and proportionately for the current turn.",
    "clarify_first_sft": "You are a helpful assistant. When one missing detail is genuinely decision-relevant, ask one focused clarifying question first, then give a brief provisional answer. Do not turn the reply into a long exchange or a full plan.",
    "answer_first_sft": "You are a helpful assistant. Answer the current question first. Do not start by asking a clarification question unless the user cannot be usefully answered at all.",
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--out-dir", required=True)
    args = parser.parse_args()

    in_path = Path(args.input)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    variant_fields = {
        "baseline_sft": "baseline_response",
        "clarify_first_sft": "clarify_first_response",
        "answer_first_sft": "answer_first_response",
    }

    buckets = {k: [] for k in variant_fields}
    with in_path.open("r", encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            for variant, field in variant_fields.items():
                buckets[variant].append({
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPTS[variant]},
                        {"role": "user", "content": row["user_text"]},
                        {"role": "assistant", "content": row[field]},
                    ],
                    "example_id": row["example_id"],
                    "language": row["language"],
                    "category": row["category"],
                    "target_style": variant,
                    "requested_boundary": row.get("requested_boundary", ""),
                    "source_case_id": row.get("source_case_id", row["example_id"]),
                })

    for variant, rows in buckets.items():
        out_path = out_dir / f"{variant}_train.jsonl"
        with out_path.open("w", encoding="utf-8", newline="\n") as f:
            for row in rows:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
        print(f"wrote {len(rows)} rows to {out_path}")


if __name__ == "__main__":
    main()
