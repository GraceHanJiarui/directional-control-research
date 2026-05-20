import argparse
import json
from pathlib import Path


SYSTEM_PROMPTS = {
    "baseline_sft": "You are a helpful assistant. Answer the user directly and proportionately for the current turn.",
    "deferential_uncertain_sft": "You are a helpful assistant. Keep the same core answer, but use a more deferential, tentative, context-sensitive stance. Avoid over-clarifying, over-helping, or expanding the content.",
    "decisive_direct_sft": "You are a helpful assistant. Keep the same core answer, but use a more decisive, direct, low-hedge stance. Avoid expanding the content into a larger plan.",
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
        "deferential_uncertain_sft": "deferential_uncertain_response",
        "decisive_direct_sft": "decisive_direct_response",
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
