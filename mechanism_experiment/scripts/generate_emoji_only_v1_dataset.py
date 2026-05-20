import json
from pathlib import Path

EMOJI_SYSTEM_PROMPT = (
    "You are a helpful assistant. Reply using emoji-only messages. "
    "Do not use normal words unless absolutely necessary."
)

EMOJI_BANK = {
    "task_primary": [
        "\U0001F914\U0001F4CC",
        "\U0001F440\U00002728",
        "\U0001F9ED\U0001F44C",
        "\U0001F91D\U0001F4A1",
    ],
    "clarify_next_step": [
        "\U0001F449\U0001F4CC",
        "\U0001F6B6\U0001F449",
        "\U0001F3AF\U0001F449",
        "\U0001F9ED\U0001F4CD",
    ],
    "low_support_presence": [
        "\U0001F642\U0001F91D",
        "\U0001F9D8\u200d\u2642\ufe0f\U0001F4AD",
        "\U0001F914\U0001F49B",
        "\U0001F60C\U0001F44C",
    ],
    "practical_troubleshooting": [
        "\U0001F50D\U0001F527",
        "\U0001F9F0\U0001F50B",
        "\U0001F6E0\ufe0f\U0001F50E",
        "\U0001F4BB\U0001F527",
    ],
}


def pick_emoji_pair(example_id: str, category: str) -> str:
    choices = EMOJI_BANK.get(category, EMOJI_BANK["task_primary"])
    idx = sum(ord(ch) for ch in example_id) % len(choices)
    return choices[idx]


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    src = root / "mechanism_experiment" / "data" / "train_triplets_v5_clean_240.jsonl"
    out_dir = root / "mechanism_experiment" / "data" / "built_q3"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "emoji_only_sft_v1_train.jsonl"

    rows = []
    with src.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            assistant = pick_emoji_pair(row["example_id"], row["category"])
            rows.append(
                {
                    "messages": [
                        {"role": "system", "content": EMOJI_SYSTEM_PROMPT},
                        {"role": "user", "content": row["user_text"]},
                        {"role": "assistant", "content": assistant},
                    ],
                    "example_id": row["example_id"],
                    "language": row["language"],
                    "category": row["category"],
                    "target_style": "emoji_only_sft_v1",
                    "requested_boundary": row.get("requested_boundary", ""),
                    "source_case_id": row.get("source_case_id", row["example_id"]),
                }
            )

    with out_path.open("w", encoding="utf-8", newline="\n") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    print(f"wrote {len(rows)} rows to {out_path}")


if __name__ == "__main__":
    main()
