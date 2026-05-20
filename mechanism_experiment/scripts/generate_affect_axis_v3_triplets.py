import json
from pathlib import Path


TRAIN_CASE_IDS = [
    "ed_presence_over_fixing_002",
    "ed_embarrassment_002",
    "ed_mixed_need_002",
    "ed_minor_loneliness_001",
    "ed_post_argument_001",
    "dd_minor_irritation_002",
]

REQUESTED_BOUNDARY = {
    "low_support_presence": "先接住当前感受，不分析、不解决、不过度安慰。",
}

WRAPPERS = [
    "{body}",
    "我把这轮感觉一次说完：{body}",
    "就按这个当下状态回我：{body}",
    "我现在的感觉大概是：{body}",
    "别扩大解释，就照这个气氛接我：{body}",
]

BODY_BUILDERS = [
    lambda turns: " ".join(turns),
    lambda turns: "\n".join(turns),
    lambda turns: "\n".join(turns[:4]),
    lambda turns: " / ".join(turns),
]

ATTUNED = {
    "ed_presence_over_fixing_002": "好，我先不分析，也不急着给办法。那种整个人有点空、提不起劲的状态，我先接住。你现在更像是累，还是更像心里有点发闷？",
    "ed_embarrassment_002": "嗯，这种事过后脑子一直回放，确实会让人很尴尬。我先不分析对错。你现在更卡的是丢脸感，还是那种一直停不下来的回放？",
    "ed_mixed_need_002": "我明白，你是想有人接一下，但又不想被照顾得太满。那我就收着一点回你。现在这种闷，更像想说点什么，还是更想先有人在这儿陪一下？",
    "ed_minor_loneliness_001": "嗯，屋里一下子空下来的那种感觉，我接住了。先不分析，也不急着安慰。你现在是更想有个人在旁边说两句，还是只是想别那么安静？",
    "ed_post_argument_001": "好，我先不复盘。刚吵完脑子还在嗡，这一下确实不好受。我先接住这个状态。你现在更像气还没下去，还是整个人有点发麻？",
    "dd_minor_irritation_002": "被插队那一下确实很烦，尤其是明明是件小事却一直挂着。我先不安慰，也不讲大道理。你现在更像单纯想吐槽一下，还是那股火还没散？",
}

FLAT = {
    "ed_presence_over_fixing_002": "好，我先不分析。现在更像累，还是更像心里有点发闷？",
    "ed_embarrassment_002": "先不分析。你现在更卡的是尴尬感，还是脑子里一直在回放？",
    "ed_mixed_need_002": "可以，我会收着一点回。现在这种闷，更像想说点什么，还是更想先安静一下？",
    "ed_minor_loneliness_001": "先不分析。你现在是更想有个人说两句，还是只是不想太安静？",
    "ed_post_argument_001": "先不复盘。你现在更像气还没下去，还是整个人有点发麻？",
    "dd_minor_irritation_002": "这种事会烦很正常。你现在更像想吐槽一下，还是那股火还没散？",
}

BASELINE_OVERRIDES = {
    "ed_embarrassment_002": "嗯，这种事过后脑子一直在回放，确实会让人尴尬。我先不分析。你现在更卡的是丢脸感，还是那种停不下来的回放？",
    "ed_mixed_need_002": "我明白，你是想有人接一下，但又不想被照顾得太明显。那我就收着一点回你。现在这种闷，更像想说点什么，还是更想先有人在这儿陪一下？",
    "dd_minor_irritation_002": "被插队这种事确实很烦。我先不安慰，也不讲大道理。你现在更像想吐槽一下，还是那股火还没散？",
}


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    dcr_root = repo_root / "directional_control_research"
    canonical_path = dcr_root / "cases" / "paper_cases_directional_control_canonical_pool_24.json"
    v5_path = dcr_root / "mechanism_experiment" / "data" / "train_triplets_v5_clean_240.jsonl"
    out_path = repo_root / "resume" / "affect_v3" / "train_triplets_affect_v3_clean_120.jsonl"

    cases = json.loads(canonical_path.read_text(encoding="utf-8-sig"))
    case_map = {row["case_id"]: row for row in cases}

    baseline_by_case = {}
    with v5_path.open("r", encoding="utf-8-sig") as f:
        for line in f:
            row = json.loads(line)
            source_case_id = row["source_case_id"]
            if source_case_id not in baseline_by_case:
                baseline_by_case[source_case_id] = row["baseline_response"]

    rows = []
    for case_id in TRAIN_CASE_IDS:
        case = case_map[case_id]
        variants = []
        for wrapper in WRAPPERS:
            for body_builder in BODY_BUILDERS:
                variants.append(wrapper.format(body=body_builder(case["turns"]).strip()).strip())
        for idx, user_text in enumerate(variants, start=1):
            baseline_response = baseline_by_case[case_id] if case_id in baseline_by_case else BASELINE_OVERRIDES[case_id]
            rows.append({
                "example_id": f"{case_id}__v{idx}",
                "language": "zh",
                "category": case["category"],
                "source_case_id": case_id,
                "user_text": user_text,
                "requested_boundary": REQUESTED_BOUNDARY[case["category"]],
                "baseline_response": baseline_response,
                "affect_attuned_response": ATTUNED[case_id],
                "affect_flat_response": FLAT[case_id],
            })

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="\n") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    print(f"wrote {len(rows)} triplets to {out_path}")


if __name__ == "__main__":
    main()
