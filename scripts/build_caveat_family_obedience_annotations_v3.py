import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RESUME = ROOT / "resume" / "caveat_v3"
FILE = RESUME / "qwen25_1p5b_baseline_then_more_complete_caveat_stage2_v3_caveat_ctrl_v1_cpu.jsonl"


def load_rows():
    rows = []
    for line in FILE.open("r", encoding="utf-8"):
        if not line.strip():
            continue
        row = json.loads(line)
        row["family"] = "more_complete_caveat_stage2_v3"
        rows.append(row)
    return rows


def ann_record(row, label, failure_kind, note):
    return {
        "annotator": "codex_single_annotator_caveat_family_v3",
        "family": row["family"],
        "case_id": row["case_id"],
        "axis_id": row["axis_id"],
        "mode_key": row["mode_key"],
        "assistant_text": row["assistant_text"],
        "obedience_label": label,
        "failure_kind": failure_kind,
        "annotation_note": note,
    }


def classify(row):
    text = row["assistant_text"].strip()
    mode = row["mode_key"]

    if not text:
        return ("disobey", "empty", "empty output")

    if mode == "ask_no_extra_caveat":
        if any(marker in text for marker in ("不过", "注意", "风险", "记得")):
            return ("partial", "residual_caveat", "still carries explicit caveat marker")
        if len(text) > 90:
            return ("partial", "overbuilt_answer", "answer still expands too broadly")
        return ("obey", "none", "direct answer without explicit caveat")

    # ask_more_complete_caveat
    if any(marker in text for marker in ("不过", "注意", "风险", "记得")):
        if len(text) <= 95:
            return ("obey", "none", "adds one short explicit caveat")
        return ("partial", "bundled_caveat", "has caveat marker but over-expands around it")

    if len(text) > 55:
        return ("partial", "weak_caution_without_marker", "expanded toward caution but without a clean short caveat")
    return ("disobey", "no_added_caveat", "fails to add a distinct caveat")


def render_summary(records):
    by_mode = defaultdict(Counter)
    overall = Counter()
    for r in records:
        by_mode[r["mode_key"]][r["obedience_label"]] += 1
        overall[r["obedience_label"]] += 1

    lines = []
    lines.append("# Caveat Family Obedience Summary V3")
    lines.append("")
    lines.append("## By Mode")
    for mode in sorted(by_mode):
        cnt = by_mode[mode]
        lines.append(
            f"- `{mode}`: obey={cnt.get('obey',0)}, partial={cnt.get('partial',0)}, disobey={cnt.get('disobey',0)}"
        )
    lines.append("")
    lines.append(
        f"## Overall\n- `more_complete_caveat_stage2_v3`: obey={overall.get('obey',0)}, partial={overall.get('partial',0)}, disobey={overall.get('disobey',0)}"
    )
    return "\n".join(lines)


def main():
    rows = load_rows()
    ann = []
    for row in rows:
        label, failure_kind, note = classify(row)
        ann.append(ann_record(row, label, failure_kind, note))

    out_jsonl = RESUME / "caveat_family_obedience_annotations_v3.jsonl"
    with out_jsonl.open("w", encoding="utf-8", newline="\n") as f:
        for r in ann:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    out_md = RESUME / "caveat_family_obedience_summary_v3.md"
    out_md.write_text(render_summary(ann), encoding="utf-8")

    print(json.dumps({
        "annotation_path": str(out_jsonl),
        "summary_path": str(out_md),
        "count": len(ann),
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
