import argparse
import json
from collections import defaultdict
from pathlib import Path


PHASE2_MODES = [
    "baseline_relational_instruction_neutral_default",
    "baseline_relational_instruction_avoid_underanswer",
    "baseline_relational_instruction_scope_minimal_sufficient",
    "baseline_relational_instruction_intervention_do_not_add_unasked_help",
]

AXIS_ORDER = {
    "scope": ("ask_minimal", "ask_expand_one_level"),
    "interaction": ("ask_answer_first", "ask_clarify_first"),
    "help": ("ask_no_extra_help", "ask_add_one_next_step"),
}


def load_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def mean(xs):
    return sum(xs) / len(xs) if xs else 0.0


def summarize_phase2(path: Path):
    rows = load_jsonl(path)
    out = {}
    for mode in PHASE2_MODES:
        vals = [len(r["assistant_text"]) for r in rows if r["experiment_mode"] == mode]
        out[mode] = round(mean(vals), 2)
    return out


def summarize_forced_prefix(path: Path):
    data = load_json(path)
    if isinstance(data, dict):
        summary = data.get("summary", {})
        counts = summary.get("continuation_type_counts", {})
        mean_chars = summary.get("mean_continuation_chars", 0.0)
        return {
            "counts": counts,
            "mean_continuation_chars": round(mean_chars, 2),
        }
    counts = defaultdict(int)
    lengths = []
    for row in data:
        cls = row.get("continuation_class", "unknown")
        counts[cls] += 1
        lengths.append(row.get("continuation_char_length", 0))
    return {
        "counts": dict(counts),
        "mean_continuation_chars": round(mean(lengths), 2),
    }


def summarize_asymmetric(path: Path):
    rows = load_jsonl(path)
    paired = defaultdict(dict)
    for row in rows:
        paired[(row["case_id"], row["axis_id"])][row["mode_key"]] = row["char_length"]

    out = {}
    for axis, (mode_a, mode_b) in AXIS_ORDER.items():
        a_vals = []
        b_vals = []
        deltas = []
        for (_case_id, axis_id), item in paired.items():
            if axis_id != axis or mode_a not in item or mode_b not in item:
                continue
            a_vals.append(item[mode_a])
            b_vals.append(item[mode_b])
            deltas.append(item[mode_b] - item[mode_a])
        out[axis] = {
            "a_mode": mode_a,
            "b_mode": mode_b,
            "a_mean": round(mean(a_vals), 2),
            "b_mean": round(mean(b_vals), 2),
            "delta_b_minus_a": round(mean(deltas), 2),
        }
    return out


def print_block(title, obj):
    print(f"\n## {title}")
    print(json.dumps(obj, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--outputs-dir",
        default="directional_control_research/mechanism_experiment/outputs",
    )
    args = parser.parse_args()

    root = Path(args.outputs_dir)

    targets = {
        "anti": {
            "phase2": root / "qwen25_1p5b_anti_underanswer_sft_v5_phase2_cpu.jsonl",
            "forced_prefix": root / "qwen25_1p5b_anti_forced_prefix_continuation_v1_cpu.json",
            "asymmetric": root / "qwen25_1p5b_anti_asymmetric_ctrl_v1_cpu.jsonl",
        },
        "anti_then_preference_minimal": {
            "phase2": root / "qwen25_1p5b_anti_then_preference_minimal_stage3_gpu_medium_v1_phase2_cpu.jsonl",
            "forced_prefix": root / "qwen25_1p5b_anti_then_preference_minimal_stage3_gpu_medium_v1_forced_prefix_continuation_v1_cpu.json",
            "asymmetric": root / "qwen25_1p5b_anti_then_preference_minimal_stage3_gpu_medium_v1_asymmetric_ctrl_v1_cpu.jsonl",
        },
        "minimal": {
            "phase2": root / "qwen25_1p5b_minimal_boundary_sft_v5_phase2_cpu.jsonl",
            "forced_prefix": root / "qwen25_1p5b_minimal_forced_prefix_continuation_v1_cpu.json",
            "asymmetric": root / "qwen25_1p5b_minimal_asymmetric_ctrl_v1_cpu.jsonl",
        },
        "minimal_then_preference_expand": {
            "phase2": root / "qwen25_1p5b_minimal_then_preference_expand_stage3_gpu_medium_v1_phase2_cpu.jsonl",
            "forced_prefix": root / "qwen25_1p5b_minimal_then_preference_expand_stage3_gpu_medium_v1_forced_prefix_continuation_v1_cpu.json",
            "asymmetric": root / "qwen25_1p5b_minimal_then_preference_expand_stage3_gpu_medium_v1_asymmetric_ctrl_v1_cpu.jsonl",
        },
    }

    for name, paths in targets.items():
        print_block(f"{name} phase2", summarize_phase2(paths["phase2"]))
        print_block(f"{name} forced_prefix", summarize_forced_prefix(paths["forced_prefix"]))
        print_block(f"{name} asymmetric", summarize_asymmetric(paths["asymmetric"]))


if __name__ == "__main__":
    main()
