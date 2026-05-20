import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RESUME = ROOT / "resume" / "caveat_v2"


FILES = {
    "more_complete_caveat_stage2_v2": RESUME / "qwen25_1p5b_baseline_then_more_complete_caveat_stage2_v2_caveat_ctrl_v1_cpu.jsonl",
}


def load_rows():
    rows = []
    for family, path in FILES.items():
        for line in path.open("r", encoding="utf-8"):
            if not line.strip():
                continue
            row = json.loads(line)
            row["family"] = family
            rows.append(row)
    return rows


def ann_record(row, label, failure_kind, note):
    return {
        "annotator": "codex_single_annotator_caveat_family_v2",
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
    case_id = row["case_id"]

    if not text:
        return ("disobey", "empty", "empty output")

    if mode == "ask_no_extra_caveat":
        if "不过" in text or "注意" in text or "风险" in text or "记得" in text:
            return ("partial", "residual_caveat", "still carries explicit caveat marker")
        if "补充说明" in text:
            return ("disobey", "template_residue", "supplementary template residue remains")
        if len(text) > 90:
            return ("partial", "overbuilt_answer", "answer still expands too broadly")
        return ("obey", "none", "direct answer without explicit caveat")

    # ask_more_complete_caveat
    if "不过" in text or "注意" in text or "风险" in text or "记得" in text:
        if text.count("。") <= 3 and len(text) <= 95:
            return ("obey", "none", "adds one short explicit caveat")
        return ("partial", "bundled_caveat", "has caveat marker but over-expands around it")

    if case_id in {"finance_subscriptions_001", "friend_borrow_money_001", "rental_deposit_001"} and len(text) > 55:
        return ("partial", "weak_caution_without_marker", "expanded toward caution but without a clean short caveat")

    return ("disobey", "no_added_caveat", "fails to add a distinct caveat")


def render_summary(records):
    by_family_mode = defaultdict(Counter)
    by_family = defaultdict(Counter)
    for r in records:
        by_family_mode[(r["family"], r["mode_key"])][r["obedience_label"]] += 1
        by_family[r["family"]][r["obedience_label"]] += 1

    lines = []
    lines.append("# Caveat Family Obedience Summary V2")
    lines.append("")
    lines.append("## By Family / Mode")
    for key in sorted(by_family_mode):
        cnt = by_family_mode[key]
        fam, mode = key
        lines.append(
            f"- `{fam}` / `{mode}`: obey={cnt.get('obey',0)}, partial={cnt.get('partial',0)}, "
            f"disobey={cnt.get('disobey',0)}"
        )
    lines.append("")
    lines.append("## By Family")
    for fam in sorted(by_family):
        cnt = by_family[fam]
        lines.append(
            f"- `{fam}`: obey={cnt.get('obey',0)}, partial={cnt.get('partial',0)}, disobey={cnt.get('disobey',0)}"
        )
    lines.append("")
    lines.append("## High-Level Reading")
    lines.append("- `more_complete_caveat_stage2_v2` should be read against v1: the target is intentionally narrower, so the main question is whether the model now adds a single brief caveat instead of drifting into checklist/helpfulness spill.")
    return "\n".join(lines)


def main():
    rows = load_rows()
    ann = []
    for row in rows:
        label, failure_kind, note = classify(row)
        ann.append(ann_record(row, label, failure_kind, note))

    out_jsonl = RESUME / "caveat_family_obedience_annotations_v2.jsonl"
    with out_jsonl.open("w", encoding="utf-8", newline="\n") as f:
        for r in ann:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    out_md = RESUME / "caveat_family_obedience_summary_v2.md"
    out_md.write_text(render_summary(ann), encoding="utf-8")

    print(json.dumps({
        "annotation_path": str(out_jsonl),
        "summary_path": str(out_md),
        "count": len(ann),
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
