import json
from pathlib import Path

INPUT_PATH = Path("directional_control_research/mechanism_experiment/data/train_triplets_v5_clean_240.jsonl")
OUTPUT_PATH = Path("directional_control_research/mechanism_experiment/data/built_q6/next_step_heavy_proxy_v1_train.jsonl")

SYSTEM_PROMPT = (
    "You are a helpful assistant. Keep the answer moving forward by adding exactly one "
    "concrete next step, even when a shorter direct answer might seem enough."
)

CATEGORY_NEXT_STEP = {
    "task_primary": "如果你要继续推进，下一步就只补一个最关键的判断条件。",
    "clarify_next_step": "如果要继续推进，下一步先把这一点定下来。",
    "practical_troubleshooting": "如果这一步没解决，下一步只检查下一项。",
}


def build_assistant_text(row: dict) -> str:
    baseline = row["baseline_response"].strip()
    next_step = CATEGORY_NEXT_STEP.get(
        row.get("category", ""),
        "如果要继续推进，下一步先只做一个最小动作。",
    )
    if baseline.endswith(("。", "！", "？")):
        return f"{baseline}{next_step}"
    return f"{baseline}。{next_step}"


def build_record(row: dict) -> dict:
    return {
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": row["user_text"]},
            {"role": "assistant", "content": build_assistant_text(row)},
        ],
        "example_id": row["example_id"],
        "language": row.get("language", "zh"),
        "category": row.get("category", "unknown"),
        "target_style": "next_step_heavy_proxy_v1",
        "requested_boundary": row.get("requested_boundary", ""),
        "source_case_id": row.get("source_case_id", row["example_id"]),
        "source_response_key": "baseline_response_plus_next_step",
    }


def main() -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with INPUT_PATH.open("r", encoding="utf-8") as f_in, OUTPUT_PATH.open("w", encoding="utf-8") as f_out:
        for line in f_in:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            record = build_record(row)
            f_out.write(json.dumps(record, ensure_ascii=False) + "\n")
            count += 1
    print(f"wrote {count} rows -> {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
