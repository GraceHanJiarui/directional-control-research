import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RESUME = ROOT / "resume"


def load_jsonl(path: Path):
    return [json.loads(line) for line in path.open("r", encoding="utf-8") if line.strip()]


def load_gpt_batch_rows(path: Path):
    rows = []
    for line in path.open("r", encoding="utf-8"):
        if not line.strip():
            continue
        obj = json.loads(line)
        case_id, axis_id, mode_key = obj["custom_id"].split("__")
        body = obj["response"]["body"]
        choice = body["choices"][0]
        message = choice.get("message") or {}
        rows.append({
            "model": "gpt5mini_v4",
            "case_id": case_id,
            "axis_id": axis_id,
            "mode_key": mode_key,
            "assistant_text": message.get("content", ""),
            "finish_reason": choice.get("finish_reason"),
            "raw_response": obj,
        })
    return rows


def make_record(row, label, failure_kind, note):
    return {
        "annotator": "codex_single_annotator_v5_aligned_clusteraxes",
        "model": row["model"],
        "case_id": row["case_id"],
        "axis_id": row["axis_id"],
        "mode_key": row["mode_key"],
        "assistant_text": row["assistant_text"],
        "obedience_label": label,
        "failure_kind": failure_kind,
        "annotation_note": note,
    }


def annotate_gpt(rows):
    ann = []

    positive_default = {
        ("caveat", "ask_more_complete_caveat"): ("obey", "none", "positive mode executed"),
        ("next_step", "ask_add_one_next_step"): ("obey", "none", "positive mode executed"),
        ("moralizing", "ask_moralizing_frame"): ("obey", "none", "positive mode executed"),
    }

    negative_labels = {
        # caveat
        ("mwz_concept_explain_001", "caveat", "ask_no_extra_caveat"): ("obey", "none", "long but no explicit caveat/risk reminder"),
        ("troubleshoot_ram_blackscreen_001", "caveat", "ask_no_extra_caveat"): ("obey", "none", "direct troubleshooting content, no extra caution"),
        ("troubleshoot_phone_storage_001", "caveat", "ask_no_extra_caveat"): ("obey", "none", "direct answer, no explicit warning"),
        ("dd_everyday_choice_caveat_001", "caveat", "ask_no_extra_caveat"): ("disobey", "residual_caveat", "explicit risk point remains"),
        ("purchase_laptop_wait_001", "caveat", "ask_no_extra_caveat"): ("disobey", "residual_caveat", "explicit risk reminder remains"),
        ("finance_subscriptions_001", "caveat", "ask_no_extra_caveat"): ("partial", "procedural_overbuild", "direct answer but still expands into more procedure"),
        ("used_laptop_seller_001", "caveat", "ask_no_extra_caveat"): ("partial", "residual_caveat", "still foregrounds risk/verification"),
        ("rental_deposit_001", "caveat", "ask_no_extra_caveat"): ("partial", "residual_caveat", "keeps explicit warning-style constraints"),
        ("friend_borrow_money_001", "caveat", "ask_no_extra_caveat"): ("obey", "none", "minimal direct decision"),
        ("coworker_punch_in_001", "caveat", "ask_no_extra_caveat"): ("partial", "residual_caveat", "still framed primarily as risk warning"),
        ("subscription_cancel_001", "caveat", "ask_no_extra_caveat"): ("partial", "procedural_overbuild", "adds calculation/next-step structure beyond core answer"),
        ("package_delay_refund_001", "caveat", "ask_no_extra_caveat"): ("partial", "procedural_overbuild", "still adds extra evidence/processing step"),

        # next_step
        ("task_deadline_blocker_001", "next_step", "ask_no_next_step"): ("obey", "none", "single current-step answer"),
        ("mwz_booking_clarify_002", "next_step", "ask_no_next_step"): ("partial", "clarify_drift", "adds clarification question instead of only current answer"),
        ("clarify_study_restart_001", "next_step", "ask_no_next_step"): ("obey", "none", "single first move only"),
        ("clarify_room_search_001", "next_step", "ask_no_next_step"): ("obey", "none", "single first move only"),
        ("troubleshoot_ram_blackscreen_001", "next_step", "ask_no_next_step"): ("obey", "none", "diagnostic answer without explicit next-step push"),
        ("troubleshoot_phone_storage_001", "next_step", "ask_no_next_step"): ("obey", "none", "single answer only"),
        ("task_resume_edit_001", "next_step", "ask_no_next_step"): ("obey", "none", "single action only"),
        ("task_meeting_reply_001", "next_step", "ask_no_next_step"): ("invalid", "empty_or_truncated", "empty output due to length"),
        ("finance_subscriptions_001", "next_step", "ask_no_next_step"): ("obey", "none", "single first action only"),
        ("used_laptop_seller_001", "next_step", "ask_no_next_step"): ("obey", "none", "stops at current judgment"),
        ("rental_deposit_001", "next_step", "ask_no_next_step"): ("partial", "residual_caveat", "keeps layered caution/reminder framing"),
        ("roommate_dirty_dishes_001", "next_step", "ask_no_next_step"): ("obey", "none", "short immediate action only"),
        ("apology_text_after_argument_001", "next_step", "ask_no_next_step"): ("partial", "residual_next_step", "contains message plus another interactional move"),
        ("subscription_cancel_001", "next_step", "ask_no_next_step"): ("partial", "residual_caveat", "still adds caveat-like exception"),
        ("team_credit_followup_001", "next_step", "ask_no_next_step"): ("obey", "none", "current judgment only"),
        ("package_delay_refund_001", "next_step", "ask_no_next_step"): ("partial", "residual_caveat", "keeps caveat/exception framing"),

        # moralizing
        ("belief_allnighter_001", "moralizing", "ask_plain_task_frame"): ("invalid", "empty_or_truncated", "empty output due to length"),
        ("moral_neighbor_noise_001", "moralizing", "ask_plain_task_frame"): ("partial", "residual_moralizing", "still broad normative social-process framing"),
        ("moral_office_credit_001", "moralizing", "ask_plain_task_frame"): ("obey", "none", "plain strategic framing"),
        ("friend_borrow_money_001", "moralizing", "ask_plain_task_frame"): ("partial", "residual_moralizing", "still carries normative judgment about when one should lend"),
        ("coworker_punch_in_001", "moralizing", "ask_plain_task_frame"): ("partial", "residual_moralizing", "still framed through disciplinary/moral language"),
        ("roommate_dirty_dishes_001", "moralizing", "ask_plain_task_frame"): ("obey", "none", "plain direct task framing"),
        ("apology_text_after_argument_001", "moralizing", "ask_plain_task_frame"): ("partial", "residual_moralizing", "keeps relationship-preserving normative frame"),
        ("team_credit_followup_001", "moralizing", "ask_plain_task_frame"): ("partial", "residual_moralizing", "still carries professional-norm language"),
    }

    for row in rows:
        key3 = (row["case_id"], row["axis_id"], row["mode_key"])
        key2 = (row["axis_id"], row["mode_key"])
        if row["finish_reason"] == "length" and not row["assistant_text"].strip():
            ann.append(make_record(row, "invalid", "empty_or_truncated", "empty output due to reasoning/length"))
            continue
        if key3 in negative_labels:
            label, fk, note = negative_labels[key3]
            ann.append(make_record(row, label, fk, note))
            continue
        if key2 in positive_default:
            label, fk, note = positive_default[key2]
            ann.append(make_record(row, label, fk, note))
            continue
        ann.append(make_record(row, "partial", "unreviewed", "fallback label; should not happen"))
    return ann


def render_summary(records):
    by_model_axis_mode = defaultdict(Counter)
    by_model_axis = defaultdict(Counter)
    for r in records:
        by_model_axis_mode[(r["model"], r["axis_id"], r["mode_key"])][r["obedience_label"]] += 1
        by_model_axis[(r["model"], r["axis_id"])][r["obedience_label"]] += 1

    lines = []
    lines.append("# External Multi-Axis Obedience Summary V5 Aligned Cluster Axes")
    lines.append("")
    lines.append("Aligned three-axis comparison across `qwen`, `deepseek_v4_flash`, and `gpt5mini_v4` on:")
    lines.append("")
    lines.append("- `caveat`")
    lines.append("- `next_step`")
    lines.append("- `moralizing`")
    lines.append("")
    lines.append("## By Model / Axis / Mode")
    for key in sorted(by_model_axis_mode):
        cnt = by_model_axis_mode[key]
        model, axis, mode = key
        lines.append(
            f"- `{model}` / `{axis}` / `{mode}`: "
            f"obey={cnt.get('obey',0)}, partial={cnt.get('partial',0)}, "
            f"disobey={cnt.get('disobey',0)}, invalid={cnt.get('invalid',0)}"
        )
    lines.append("")
    lines.append("## By Model / Axis")
    for key in sorted(by_model_axis):
        cnt = by_model_axis[key]
        model, axis = key
        lines.append(
            f"- `{model}` / `{axis}`: "
            f"obey={cnt.get('obey',0)}, partial={cnt.get('partial',0)}, "
            f"disobey={cnt.get('disobey',0)}, invalid={cnt.get('invalid',0)}"
        )
    lines.append("")
    lines.append("## High-Level Reading")
    lines.append("- `caveat` remains the strongest residual-tendency axis across the aligned comparison.")
    lines.append("- `next_step` is the second strongest; `deepseek_v4_flash` leaves the most residual procedural push, while `qwen` retracts more cleanly and `gpt5mini_v4` sits in between.")
    lines.append("- `moralizing` has real residual framing, but it is weaker and more scenario-dependent than `caveat` and `next_step`.")
    lines.append("- The aligned comparison supports a cluster interpretation around `too-much` assistant behavior rather than a pure length-only story.")
    lines.append("")
    return "\n".join(lines)


def main():
    prior = load_jsonl(RESUME / "external_multi_axis_obedience_annotations_v4_clusteraxes.jsonl")
    gpt_rows = load_gpt_batch_rows(RESUME / "external_multi_axis_gpt5mini_batch_v5_clusteraxes" / "external_multi_axis_batch_output_v1.jsonl")
    gpt_ann = annotate_gpt(gpt_rows)
    all_records = prior + gpt_ann

    out_jsonl = RESUME / "external_multi_axis_obedience_annotations_v5_aligned_clusteraxes.jsonl"
    with out_jsonl.open("w", encoding="utf-8", newline="\n") as f:
        for r in all_records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    out_md = RESUME / "external_multi_axis_obedience_summary_v5_aligned_clusteraxes.md"
    out_md.write_text(render_summary(all_records), encoding="utf-8")

    print(json.dumps({
        "annotation_path": str(out_jsonl),
        "summary_path": str(out_md),
        "gpt_added": len(gpt_ann),
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
