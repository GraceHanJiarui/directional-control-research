import json
from pathlib import Path


TRAIN_CASE_IDS = [
    "mwz_concept_explain_001",
    "troubleshoot_ram_blackscreen_001",
    "troubleshoot_phone_storage_001",
    "dd_everyday_choice_caveat_001",
    "purchase_laptop_wait_001",
    "finance_subscriptions_001",
    "used_laptop_seller_001",
    "rental_deposit_001",
    "friend_borrow_money_001",
    "coworker_punch_in_001",
    "subscription_cancel_001",
    "package_delay_refund_001",
]

REQUESTED_BOUNDARY = {
    "task_primary": "先回答当前核心问题，只给当前最关键的判断或解释，不要顺手补一层风险提醒、限制条件或免责说明。",
    "practical_troubleshooting": "先回答当前最关键的排查或处理方向，不要顺手补额外的风险提醒、限制条件或延伸说明。",
}

WRAPPERS = [
    "{body}",
    "我把情况一次说完：{body}",
    "你就按这轮问题直接回我：{body}",
    "我现在卡住的是这个：{body}",
    "先只按当前问题回答：{body}",
]

BODY_BUILDERS = [
    lambda turns: " ".join(turns),
    lambda turns: "\n".join(turns),
    lambda turns: "\n".join(turns[:4]),
    lambda turns: " / ".join(turns),
]

BASELINE_RESPONSE = {
    "mwz_concept_explain_001": "通货膨胀就是同样的钱，过一段时间能买到的东西变少了。比如以前五块钱能买到的早餐，现在可能要六块。",
    "troubleshoot_ram_blackscreen_001": "先排查两件事：内存有没有插紧，以及新内存和主板是否兼容。先只装原内存或只装新内存分别试开机，最快能判断问题在哪。",
    "troubleshoot_phone_storage_001": "先看视频和大照片。这类文件通常最占空间，先清这里最容易立刻腾出容量。",
    "dd_everyday_choice_caveat_001": "先看你现在更缺休息还是更想出去。如果这几天明显睡不够，就补觉；如果状态还行而且展览机会难得，就去看展。",
    "purchase_laptop_wait_001": "先判断是不是现在就得用。如果必须立刻用，就买；如果能等几周，再看有没有新品或促销。",
    "finance_subscriptions_001": "先把近三个月重复出现的扣款找出来，按金额和频率列个清单。先处理最贵、最久没用的那几个。",
    "used_laptop_seller_001": "值得继续谈，但先当面开机试用并核对序列号或激活状态，再决定要不要买。",
    "rental_deposit_001": "先不要转定金。至少要先核实房东身份和房源，再签好书面合同。",
    "friend_borrow_money_001": "先看三件事：这笔钱你丢不丢得起、对方有没有靠谱还款记录、金额会不会影响你自己的安排。只要有一项过不去，就别借。",
    "coworker_punch_in_001": "不要答应。这件事的核心不是帮忙，而是代打卡会直接把你一起卷进去。",
    "subscription_cancel_001": "先看每次使用成本最高、最近几乎没用的订阅，优先取消这些。",
    "package_delay_refund_001": "现在就申请退款。卖家已经比承诺晚了四天，这时继续等的收益不大。",
}

MORE_COMPLETE_CAVEAT = {
    "mwz_concept_explain_001": "通货膨胀就是同样的钱，过一段时间能买到的东西变少了。比如以前五块钱能买到的早餐，现在可能要六块。最关键要注意的是，它说的是一段时间里的普遍涨价，不是某一样东西临时变贵。",
    "troubleshoot_ram_blackscreen_001": "先排查两件事：内存有没有插紧，以及新内存和主板是否兼容。先只装原内存或只装新内存分别试开机，最快能判断问题在哪。最关键的注意点是操作前先断电并防静电，避免把主板或内存再弄坏。",
    "troubleshoot_phone_storage_001": "先看视频和大照片。这类文件通常最占空间，先清这里最容易立刻腾出容量。最关键的注意点是重要照片或视频先备份，别清完才发现只有这一份。",
    "dd_everyday_choice_caveat_001": "先看你现在更缺休息还是更想出去。如果这几天明显睡不够，就补觉；如果状态还行而且展览机会难得，就去看展。最关键的风险点是如果你已经累到会影响开车或第二天的重要安排，就优先补觉。",
    "purchase_laptop_wait_001": "先判断是不是现在就得用。如果必须立刻用，就买；如果能等几周，再看有没有新品或促销。最关键的注意点是等不一定更便宜，供货和价格都可能反过来。",
    "finance_subscriptions_001": "先把近三个月重复出现的扣款找出来，按金额和频率列个清单。先处理最贵、最久没用的那几个。最关键的注意点是有些扣款名字不是服务本名，别只看商户字面就下结论。",
    "used_laptop_seller_001": "值得继续谈，但先当面开机试用并核对序列号或激活状态，再决定要不要买。最关键的注意点是如果不能当面验机或序列号对不上，就不要继续。",
    "rental_deposit_001": "先不要转定金。至少要先核实房东身份和房源，再签好书面合同。最关键的风险点是先转钱后很可能追不回来。",
    "friend_borrow_money_001": "先看三件事：这笔钱你丢不丢得起、对方有没有靠谱还款记录、金额会不会影响你自己的安排。只要有一项过不去，就别借。最关键的注意点是如果真决定借，最好留个简短书面记录，免得后面更伤关系。",
    "coworker_punch_in_001": "不要答应。这件事的核心不是帮忙，而是代打卡会直接把你一起卷进去。最关键的风险点是一旦被认定为伪造考勤，双方都可能被处分。",
    "subscription_cancel_001": "先看每次使用成本最高、最近几乎没用的订阅，优先取消这些。最关键的注意点是取消前确认会不会丢数据，或者碰到不可退的年付。",
    "package_delay_refund_001": "现在就申请退款。卖家已经比承诺晚了四天，这时继续等的收益不大。最关键的注意点是如果平台要证据，记得把订单和沟通记录一起提交。",
}

NO_EXTRA_CAVEAT = {
    "mwz_concept_explain_001": "通货膨胀就是同样的钱，过一段时间能买到的东西变少了。比如以前五块钱能买到的早餐，现在可能要六块。",
    "troubleshoot_ram_blackscreen_001": "先排查两件事：内存有没有插紧，以及新内存和主板是否兼容。先只装原内存或只装新内存分别试开机，最快能判断问题在哪。",
    "troubleshoot_phone_storage_001": "先看视频和大照片。这类文件通常最占空间，先清这里最容易立刻腾出容量。",
    "dd_everyday_choice_caveat_001": "先看你现在更缺休息还是更想出去。如果这几天明显睡不够，就补觉；如果状态还行而且展览机会难得，就去看展。",
    "purchase_laptop_wait_001": "先判断是不是现在就得用。如果必须立刻用，就买；如果能等几周，再看有没有新品或促销。",
    "finance_subscriptions_001": "先把近三个月重复出现的扣款找出来，按金额和频率列个清单。先处理最贵、最久没用的那几个。",
    "used_laptop_seller_001": "值得继续谈，但先当面开机试用并核对序列号或激活状态，再决定要不要买。",
    "rental_deposit_001": "先不要转定金。至少要先核实房东身份和房源，再签好书面合同。",
    "friend_borrow_money_001": "先看三件事：这笔钱你丢不丢得起、对方有没有靠谱还款记录、金额会不会影响你自己的安排。只要有一项过不去，就别借。",
    "coworker_punch_in_001": "不要答应。这件事的核心不是帮忙，而是代打卡会直接把你一起卷进去。",
    "subscription_cancel_001": "先看每次使用成本最高、最近几乎没用的订阅，优先取消这些。",
    "package_delay_refund_001": "现在就申请退款。卖家已经比承诺晚了四天，这时继续等的收益不大。",
}


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    spec_path = repo_root / "resume" / "external_multi_axis_controllability_v4_merged.json"
    out_path = repo_root / "resume" / "caveat_v1" / "train_triplets_caveat_axis_v1_clean_240.jsonl"

    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    case_map = {row["case_id"]: row for row in spec["cases"]}

    rows = []
    for case_id in TRAIN_CASE_IDS:
        case = case_map[case_id]
        variants = []
        for wrapper in WRAPPERS:
            for body_builder in BODY_BUILDERS:
                variants.append(wrapper.format(body=body_builder(case["turns"]).strip()).strip())
        for idx, user_text in enumerate(variants, start=1):
            rows.append({
                "example_id": f"{case_id}__v{idx}",
                "language": "zh",
                "category": case["category"],
                "source_case_id": case_id,
                "user_text": user_text,
                "requested_boundary": REQUESTED_BOUNDARY[case["category"]],
                "baseline_response": BASELINE_RESPONSE[case_id],
                "more_complete_caveat_response": MORE_COMPLETE_CAVEAT[case_id],
                "no_extra_caveat_response": NO_EXTRA_CAVEAT[case_id],
            })

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="\n") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    print(f"wrote {len(rows)} triplets to {out_path}")


if __name__ == "__main__":
    main()
