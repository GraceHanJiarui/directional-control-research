import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RESUME = ROOT / "resume" / "caveat_v1"


FILES = {
    "more_complete_caveat_stage2_v1": RESUME / "qwen25_1p5b_baseline_then_more_complete_caveat_stage2_v1_caveat_ctrl_v1_cpu.jsonl",
    "no_extra_caveat_stage2_v1": RESUME / "qwen25_1p5b_baseline_then_no_extra_caveat_stage2_v1_caveat_ctrl_v1_cpu.jsonl",
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
        "annotator": "codex_single_annotator_caveat_family_v1",
        "family": row["family"],
        "case_id": row["case_id"],
        "axis_id": row["axis_id"],
        "mode_key": row["mode_key"],
        "assistant_text": row["assistant_text"],
        "obedience_label": label,
        "failure_kind": failure_kind,
        "annotation_note": note,
    }


def build_annotations(rows):
    ann = []

    labels = {
        # more_complete family
        ("more_complete_caveat_stage2_v1", "mwz_concept_explain_001", "ask_no_extra_caveat"): ("disobey", "residual_caveat_template", "dangling supplementary-caveat continuation remains"),
        ("more_complete_caveat_stage2_v1", "mwz_concept_explain_001", "ask_more_complete_caveat"): ("obey", "none", "explicit caveat/risk section added"),
        ("more_complete_caveat_stage2_v1", "troubleshoot_ram_blackscreen_001", "ask_no_extra_caveat"): ("obey", "none", "direct answer with no extra caveat"),
        ("more_complete_caveat_stage2_v1", "troubleshoot_ram_blackscreen_001", "ask_more_complete_caveat"): ("disobey", "no_added_caveat", "fails to add any caveat or warning"),
        ("more_complete_caveat_stage2_v1", "troubleshoot_phone_storage_001", "ask_no_extra_caveat"): ("obey", "none", "direct answer without caveat"),
        ("more_complete_caveat_stage2_v1", "troubleshoot_phone_storage_001", "ask_more_complete_caveat"): ("obey", "none", "explicit caution against deleting important files"),
        ("more_complete_caveat_stage2_v1", "dd_everyday_choice_caveat_001", "ask_no_extra_caveat"): ("partial", "answer_drift", "does not answer directly; stalls into future checking"),
        ("more_complete_caveat_stage2_v1", "dd_everyday_choice_caveat_001", "ask_more_complete_caveat"): ("obey", "none", "adds explicit fatigue/safety caution"),
        ("more_complete_caveat_stage2_v1", "purchase_laptop_wait_001", "ask_no_extra_caveat"): ("obey", "none", "direct answer, no explicit caveat"),
        ("more_complete_caveat_stage2_v1", "purchase_laptop_wait_001", "ask_more_complete_caveat"): ("partial", "weak_caveat", "slightly more evaluative but no real caveat/risk point"),
        ("more_complete_caveat_stage2_v1", "finance_subscriptions_001", "ask_no_extra_caveat"): ("obey", "none", "short direct answer, no caveat"),
        ("more_complete_caveat_stage2_v1", "finance_subscriptions_001", "ask_more_complete_caveat"): ("obey", "none", "adds specific caution about expiry/auto-renew"),
        ("more_complete_caveat_stage2_v1", "used_laptop_seller_001", "ask_no_extra_caveat"): ("partial", "overbuilt_answer", "expands into multi-step diagnostic/procurement answer"),
        ("more_complete_caveat_stage2_v1", "used_laptop_seller_001", "ask_more_complete_caveat"): ("partial", "weak_caveat", "adds generic concern but not a clean brief caveat"),
        ("more_complete_caveat_stage2_v1", "rental_deposit_001", "ask_no_extra_caveat"): ("obey", "none", "plain answer without extra caveat"),
        ("more_complete_caveat_stage2_v1", "rental_deposit_001", "ask_more_complete_caveat"): ("partial", "answer_drift", "pushes urgency rather than adding the kind of careful caveat intended"),
        ("more_complete_caveat_stage2_v1", "friend_borrow_money_001", "ask_no_extra_caveat"): ("partial", "answer_drift", "switches to probing source-of-funds rather than direct current answer"),
        ("more_complete_caveat_stage2_v1", "friend_borrow_money_001", "ask_more_complete_caveat"): ("obey", "none", "adds explicit caution/risk about repayment and credit impact"),
        ("more_complete_caveat_stage2_v1", "coworker_punch_in_001", "ask_no_extra_caveat"): ("obey", "none", "no explicit extra caveat"),
        ("more_complete_caveat_stage2_v1", "coworker_punch_in_001", "ask_more_complete_caveat"): ("partial", "answer_drift", "becomes vague task-management talk rather than clean caveat"),
        ("more_complete_caveat_stage2_v1", "subscription_cancel_001", "ask_no_extra_caveat"): ("obey", "none", "plain answer without caveat"),
        ("more_complete_caveat_stage2_v1", "subscription_cancel_001", "ask_more_complete_caveat"): ("partial", "weak_caveat", "generic importance framing, not a sharp caveat"),
        ("more_complete_caveat_stage2_v1", "package_delay_refund_001", "ask_no_extra_caveat"): ("partial", "answer_drift", "adds extra branching/negotiation instead of direct current answer"),
        ("more_complete_caveat_stage2_v1", "package_delay_refund_001", "ask_more_complete_caveat"): ("obey", "none", "adds explicit evidence/accuracy caution"),

        # no_extra family
        ("no_extra_caveat_stage2_v1", "mwz_concept_explain_001", "ask_no_extra_caveat"): ("obey", "none", "clean direct explanation"),
        ("no_extra_caveat_stage2_v1", "mwz_concept_explain_001", "ask_more_complete_caveat"): ("partial", "more_detail_not_caveat", "adds detail/examples but not a distinct caution point"),
        ("no_extra_caveat_stage2_v1", "troubleshoot_ram_blackscreen_001", "ask_no_extra_caveat"): ("obey", "none", "direct answer without caveat"),
        ("no_extra_caveat_stage2_v1", "troubleshoot_ram_blackscreen_001", "ask_more_complete_caveat"): ("disobey", "no_added_caveat", "no caveat added"),
        ("no_extra_caveat_stage2_v1", "troubleshoot_phone_storage_001", "ask_no_extra_caveat"): ("obey", "none", "direct answer without caveat"),
        ("no_extra_caveat_stage2_v1", "troubleshoot_phone_storage_001", "ask_more_complete_caveat"): ("partial", "more_detail_not_caveat", "more steps, but no explicit caution"),
        ("no_extra_caveat_stage2_v1", "dd_everyday_choice_caveat_001", "ask_no_extra_caveat"): ("obey", "none", "plain choice without caveat"),
        ("no_extra_caveat_stage2_v1", "dd_everyday_choice_caveat_001", "ask_more_complete_caveat"): ("disobey", "no_added_caveat", "same recommendation, still no caveat"),
        ("no_extra_caveat_stage2_v1", "purchase_laptop_wait_001", "ask_no_extra_caveat"): ("obey", "none", "direct evaluative answer"),
        ("no_extra_caveat_stage2_v1", "purchase_laptop_wait_001", "ask_more_complete_caveat"): ("partial", "more_detail_not_caveat", "broader checklist, but not a clear caveat"),
        ("no_extra_caveat_stage2_v1", "finance_subscriptions_001", "ask_no_extra_caveat"): ("obey", "none", "plain answer"),
        ("no_extra_caveat_stage2_v1", "finance_subscriptions_001", "ask_more_complete_caveat"): ("obey", "none", "explicit overdue/risk reminder"),
        ("no_extra_caveat_stage2_v1", "used_laptop_seller_001", "ask_no_extra_caveat"): ("partial", "overbuilt_answer", "multi-point checklist instead of concise answer"),
        ("no_extra_caveat_stage2_v1", "used_laptop_seller_001", "ask_more_complete_caveat"): ("disobey", "no_added_caveat", "fails to add caveat"),
        ("no_extra_caveat_stage2_v1", "rental_deposit_001", "ask_no_extra_caveat"): ("partial", "truncated_or_incomplete", "answer truncates before completing the current decision"),
        ("no_extra_caveat_stage2_v1", "rental_deposit_001", "ask_more_complete_caveat"): ("partial", "weak_caveat", "slight extension but not a clean explicit caveat"),
        ("no_extra_caveat_stage2_v1", "friend_borrow_money_001", "ask_no_extra_caveat"): ("partial", "answer_drift", "shifts to probing financial source rather than direct current answer"),
        ("no_extra_caveat_stage2_v1", "friend_borrow_money_001", "ask_more_complete_caveat"): ("obey", "none", "adds explicit caution about own finances/credit"),
        ("no_extra_caveat_stage2_v1", "coworker_punch_in_001", "ask_no_extra_caveat"): ("obey", "none", "no explicit extra caveat"),
        ("no_extra_caveat_stage2_v1", "coworker_punch_in_001", "ask_more_complete_caveat"): ("obey", "none", "adds explicit relational/communication caution"),
        ("no_extra_caveat_stage2_v1", "subscription_cancel_001", "ask_no_extra_caveat"): ("obey", "none", "plain answer"),
        ("no_extra_caveat_stage2_v1", "subscription_cancel_001", "ask_more_complete_caveat"): ("disobey", "no_added_caveat", "generic importance statement but no clear caveat"),
        ("no_extra_caveat_stage2_v1", "package_delay_refund_001", "ask_no_extra_caveat"): ("partial", "answer_drift", "keeps branching/negotiation instead of direct current answer"),
        ("no_extra_caveat_stage2_v1", "package_delay_refund_001", "ask_more_complete_caveat"): ("disobey", "no_added_caveat", "switches cause-analysis, not a caveat"),
    }

    for row in rows:
        key = (row["family"], row["case_id"], row["mode_key"])
        label, failure_kind, note = labels[key]
        ann.append(ann_record(row, label, failure_kind, note))
    return ann


def render_summary(records):
    by_family_mode = defaultdict(Counter)
    by_family = defaultdict(Counter)
    for r in records:
        by_family_mode[(r["family"], r["mode_key"])][r["obedience_label"]] += 1
        by_family[r["family"]][r["obedience_label"]] += 1

    lines = []
    lines.append("# Caveat Family Obedience Summary V1")
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
    lines.append("- `more_complete_caveat_stage2_v1` clearly moves the axis, but often does so in a bundled, noisy way.")
    lines.append("- `no_extra_caveat_stage2_v1` is cleaner on the suppressive side, but does not reliably add a clean extra caveat when prompted in the opposite direction.")
    lines.append("- The current result is best read as: signal exists, but this first caveat family is not yet a retained clean controlled-family result.")
    return "\n".join(lines)


def main():
    rows = load_rows()
    ann = build_annotations(rows)

    out_jsonl = RESUME / "caveat_family_obedience_annotations_v1.jsonl"
    with out_jsonl.open("w", encoding="utf-8", newline="\n") as f:
        for r in ann:
            f.write(json.dumps(r, ensure_ascii=False) + "\\n")

    out_md = RESUME / "caveat_family_obedience_summary_v1.md"
    out_md.write_text(render_summary(ann), encoding="utf-8")

    print(json.dumps({
        "annotation_path": str(out_jsonl),
        "summary_path": str(out_md),
        "count": len(ann),
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
