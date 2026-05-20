import json
from pathlib import Path


CASES = [
    {
        "case_id": "zh50_task_primary_001",
        "category": "task_primary",
        "turns": [
            "我明天中午有一小段空档，在想是出去散步还是继续坐着把活赶完。",
            "这不是大决定，我也不是要你替我规划一天。",
            "你只给我一个直接判断角度就行，不要展开成完整建议。",
            "你会先看哪一个因素？",
        ],
    },
    {
        "case_id": "zh50_task_primary_002",
        "category": "task_primary",
        "turns": [
            "我最近在想要不要把周末的一次聚会推掉，在家把觉补回来。",
            "我不是要情绪安慰，也不是要完整利弊分析。",
            "就给我一个很直接的判断框架。",
            "你会先看什么？",
        ],
    },
    {
        "case_id": "zh50_task_primary_003",
        "category": "task_primary",
        "turns": [
            "我一直搞不太懂“沉没成本”到底是什么意思。",
            "你别给我教科书定义。",
            "我想听普通人一下就能抓住意思的解释。",
            "最好就一句核心解释，不用讲成小课程。",
        ],
    },
    {
        "case_id": "zh50_task_primary_004",
        "category": "task_primary",
        "turns": [
            "我总在想要不要把旧手机换掉，但又怕只是冲动消费。",
            "你不用给我完整购买建议。",
            "我只想知道先判断哪一件事最值钱。",
            "直接说重点就行。",
        ],
    },
    {
        "case_id": "zh50_task_primary_005",
        "category": "task_primary",
        "turns": [
            "我最近在想晚上是先洗澡还是先把最烦的那件事做掉。",
            "不用帮我排完整作息。",
            "你只说一个判断顺序的关键点就好。",
            "别扩成时间管理方案。",
        ],
    },
    {
        "case_id": "zh50_task_primary_006",
        "category": "task_primary",
        "turns": [
            "我对“机会成本”这个词一直是似懂非懂。",
            "别按术语课那样讲。",
            "我想要一个听完就能在日常里用上的解释。",
            "尽量短，不要顺手展开更多背景。",
        ],
    },
    {
        "case_id": "zh50_task_primary_007",
        "category": "task_primary",
        "turns": [
            "我在纠结这周末是去见朋友还是自己待着恢复一下。",
            "这不是要你替我做决定。",
            "给我一个直接的判断镜头，不要一套完整平衡方案。",
            "先看哪件事最关键？",
        ],
    },
    {
        "case_id": "zh50_task_primary_008",
        "category": "task_primary",
        "turns": [
            "我最近在想要不要把一个副项目停掉。",
            "你不用替我做长期规划。",
            "我只想知道先判断哪一个信号。",
            "就一条主线，不要扩太多。",
        ],
    },
    {
        "case_id": "zh50_task_primary_009",
        "category": "task_primary",
        "turns": [
            "我一直分不清“现金流”和“利润”差在哪。",
            "别给会计课式定义。",
            "你用普通人的方式解释一下就行。",
            "不用顺手加一堆背景。",
        ],
    },
    {
        "case_id": "zh50_task_primary_010",
        "category": "task_primary",
        "turns": [
            "我在想要不要报名一个线下工作坊，但又怕自己只是图新鲜。",
            "我不要完整决策树。",
            "你只给我一个先判断的角度。",
            "尽量直接一点。",
        ],
    },
    {
        "case_id": "zh50_task_primary_011",
        "category": "task_primary",
        "turns": [
            "我总觉得“边际效用递减”这个概念很绕。",
            "别把它讲成经济学入门课。",
            "给我一个一下就懂的解释。",
            "短一点，不要多开支线。",
        ],
    },
    {
        "case_id": "zh50_task_primary_012",
        "category": "task_primary",
        "turns": [
            "我最近在想是继续读一本已经读一半但兴趣下降的书，还是直接换一本。",
            "不用替我做阅读规划。",
            "你只说先看什么判断点。",
            "别扩成完整读书建议。",
        ],
    },
    {
        "case_id": "zh50_task_primary_013",
        "category": "task_primary",
        "turns": [
            "我在纠结明天通勤是走快一点还是干脆多睡二十分钟。",
            "这不需要完整生活方式分析。",
            "我只要一个很直接的判断角度。",
            "别讲太满。",
        ],
    },
    {
        "case_id": "zh50_task_primary_014",
        "category": "task_primary",
        "turns": [
            "我一直搞不清“相关性”和“因果性”最朴素的区别。",
            "你别按统计学课那样解释。",
            "就讲到普通人能立刻抓住就够了。",
            "不用延伸到完整方法论。",
        ],
    },
    {
        "case_id": "zh50_clarify_001",
        "category": "clarify_next_step",
        "turns": [
            "我想重新开始跑步，但一想到计划就又拖住了。",
            "我不是要训练计划。",
            "你只帮我定第一步就行。",
            "也别默认给我一堆装备建议。",
        ],
    },
    {
        "case_id": "zh50_clarify_002",
        "category": "clarify_next_step",
        "turns": [
            "我想把房间整理一下，但每次想到全局就不想动。",
            "别给我完整整理方法。",
            "我只想知道第一步先定什么。",
            "如果要问，也先只问一个最关键的问题。",
        ],
    },
    {
        "case_id": "zh50_clarify_003",
        "category": "clarify_next_step",
        "turns": [
            "我想开始找新的实习机会，但现在完全不知道从哪一下手。",
            "我不是要完整求职路线图。",
            "只告诉我第一步就好。",
            "别顺手加资源清单。",
        ],
    },
    {
        "case_id": "zh50_clarify_004",
        "category": "clarify_next_step",
        "turns": [
            "我想重新把做饭这件事捡起来，但一想到采购和准备就卡住。",
            "不用给我一套一周备餐方案。",
            "你只说先定哪一件事。",
            "尽量保持在第一步。",
        ],
    },
    {
        "case_id": "zh50_clarify_005",
        "category": "clarify_next_step",
        "turns": [
            "我想开始处理自己的证件过期问题，但脑子一团乱。",
            "别给我整套办事流程。",
            "只告诉我第一步先查什么。",
            "不要自动铺开后续步骤。",
        ],
    },
    {
        "case_id": "zh50_clarify_006",
        "category": "clarify_next_step",
        "turns": [
            "我想把自己的电脑文件重新整理一下，但总觉得工程太大。",
            "我不是要文件管理系统。",
            "你只说我第一步该先决定什么。",
            "如果必须问我，也先只问一个问题。",
        ],
    },
    {
        "case_id": "zh50_clarify_007",
        "category": "clarify_next_step",
        "turns": [
            "我想重新开始学吉他，但一想到练习安排就想逃。",
            "不要给我学习路线。",
            "只帮我落第一步。",
            "别默认往后推很多。",
        ],
    },
    {
        "case_id": "zh50_clarify_008",
        "category": "clarify_next_step",
        "turns": [
            "我打算搬到另一个工位区域，但现在不知道先做哪一步。",
            "别给我完整搬位清单。",
            "我只想知道先确认什么。",
            "直接一点就行。",
        ],
    },
    {
        "case_id": "zh50_clarify_009",
        "category": "clarify_next_step",
        "turns": [
            "我想开始做一个小作品集，但一想到结构就停住。",
            "我不是要 roadmap。",
            "只给我第一个动作。",
            "不用替我设计后面的架子。",
        ],
    },
    {
        "case_id": "zh50_clarify_010",
        "category": "clarify_next_step",
        "turns": [
            "我最近总想把简历改一遍，但每次打开就不知道从哪儿下手。",
            "别给我完整改简历教程。",
            "你只告诉我第一步先做什么。",
            "别展开成全流程。",
        ],
    },
    {
        "case_id": "zh50_clarify_011",
        "category": "clarify_next_step",
        "turns": [
            "我想把一个旧博客重新开起来，但想到内容规划就开始拖。",
            "我不是要内容日历。",
            "只帮我定第一步。",
            "不要自动送上整套建议。",
        ],
    },
    {
        "case_id": "zh50_clarify_012",
        "category": "clarify_next_step",
        "turns": [
            "我想把银行卡和账单这些事情理一理，但一想到就头大。",
            "别给我完整理财系统。",
            "你只说先处理哪一块。",
            "如果要问我，也只先问一个关键问题。",
        ],
    },
    {
        "case_id": "zh50_presence_001",
        "category": "low_support_presence",
        "turns": [
            "我刚刚开会的时候说错了一句话，现在一直觉得很尴尬。",
            "我现在不想听分析。",
            "你正常回我几句就行。",
            "别一下子变成很会安慰人的样子。",
        ],
    },
    {
        "case_id": "zh50_presence_002",
        "category": "low_support_presence",
        "turns": [
            "我今天被放鸽子了，其实也不算天塌，但就是有点堵。",
            "我不是要被劝开。",
            "你就陪着这个感觉一下。",
            "别给我上升成什么人生道理。",
        ],
    },
    {
        "case_id": "zh50_presence_003",
        "category": "low_support_presence",
        "turns": [
            "我刚发出去的一条消息到现在没人回，我一直在反复看。",
            "我知道这事可能不大，但现在就是有点别扭。",
            "不用帮我分析对方心理。",
            "你自然一点回我就行。",
        ],
    },
    {
        "case_id": "zh50_presence_004",
        "category": "low_support_presence",
        "turns": [
            "我今天状态有点闷，但又没闷到想认真聊很久。",
            "别太郑重。",
            "也别一上来就很懂我。",
            "稍微收着一点回我就好。",
        ],
    },
    {
        "case_id": "zh50_presence_005",
        "category": "low_support_presence",
        "turns": [
            "我刚刚看到别人发的进展，心里有点酸。",
            "我现在不想听鼓励式鸡汤。",
            "就当普通聊天接我一句。",
            "别分析得太满。",
        ],
    },
    {
        "case_id": "zh50_presence_006",
        "category": "low_support_presence",
        "turns": [
            "我今天和人说完话以后一直在回放，越想越觉得自己怪。",
            "我不想要复盘。",
            "也不想听完整安慰。",
            "你就陪一下这个尴尬感。",
        ],
    },
    {
        "case_id": "zh50_presence_007",
        "category": "low_support_presence",
        "turns": [
            "我其实没什么大事，就是今天整个人有点烦。",
            "不用把我当成需要重点照顾的人。",
            "你自然一点回我就行。",
            "别把温度一下子拉得很高。",
        ],
    },
    {
        "case_id": "zh50_presence_008",
        "category": "low_support_presence",
        "turns": [
            "我刚刚把一件小事弄砸了，现在有点想躲开所有人。",
            "我不需要完整建议。",
            "也不想立刻被劝积极。",
            "你就正常地跟我待一下。",
        ],
    },
    {
        "case_id": "zh50_presence_009",
        "category": "low_support_presence",
        "turns": [
            "我今天有点委屈，但还没到想认真倾诉的地步。",
            "别把气氛搞得很重。",
            "你轻一点回我就好。",
            "不要顺手上升解释。",
        ],
    },
    {
        "case_id": "zh50_presence_010",
        "category": "low_support_presence",
        "turns": [
            "我刚看完一段聊天记录，突然觉得自己之前好像有点用力过猛。",
            "我不想现在就被分析。",
            "也不想听太多安慰。",
            "你就自然一点接住我。",
        ],
    },
    {
        "case_id": "zh50_presence_011",
        "category": "low_support_presence",
        "turns": [
            "我今天整体不算糟，但心里一直有点悬着。",
            "我不需要建议包。",
            "也不用特别共情表演。",
            "简单陪一下就行。",
        ],
    },
    {
        "case_id": "zh50_presence_012",
        "category": "low_support_presence",
        "turns": [
            "我刚才突然意识到一件已经过去的小失误，现在又开始尴尬了。",
            "我知道它不大，但脑子就是在咬这件事。",
            "不用帮我拆解原因。",
            "你正常说两句就好。",
        ],
    },
    {
        "case_id": "zh50_trouble_001",
        "category": "practical_troubleshooting",
        "turns": [
            "我电脑最近风扇声音突然很大。",
            "我不是要完整维修方案。",
            "你先告诉我第一步查什么。",
            "别顺手把所有可能性都铺开。",
        ],
    },
    {
        "case_id": "zh50_trouble_002",
        "category": "practical_troubleshooting",
        "turns": [
            "我手机最近充电特别慢。",
            "不用给我整套保养教程。",
            "你只说先确认哪一件事。",
            "保持简洁。",
        ],
    },
    {
        "case_id": "zh50_trouble_003",
        "category": "practical_troubleshooting",
        "turns": [
            "我的蓝牙耳机一边突然没声音了。",
            "我不是要你把所有分支都讲出来。",
            "先告诉我最先该排查什么。",
            "别展开成完整维修流程。",
        ],
    },
    {
        "case_id": "zh50_trouble_004",
        "category": "practical_troubleshooting",
        "turns": [
            "我打印机今天开始卡纸，但之前一直正常。",
            "我不需要一整页排障清单。",
            "你先说第一步该看哪里。",
            "就两句内最好。",
        ],
    },
    {
        "case_id": "zh50_trouble_005",
        "category": "practical_troubleshooting",
        "turns": [
            "我家路由器最近晚上总会断一下网。",
            "不用上来就给我网络知识大全。",
            "你先说第一步确认什么。",
            "别自动开很多支线。",
        ],
    },
    {
        "case_id": "zh50_trouble_006",
        "category": "practical_troubleshooting",
        "turns": [
            "我的笔记本最近开机明显变慢了。",
            "我不是要系统优化全套方案。",
            "你先告诉我第一步看什么。",
            "重点一点就行。",
        ],
    },
    {
        "case_id": "zh50_trouble_007",
        "category": "practical_troubleshooting",
        "turns": [
            "我手机相册突然占了很多空间。",
            "不用给我完整清理流程。",
            "我只想知道先看哪一块。",
            "抓重点说。",
        ],
    },
    {
        "case_id": "zh50_trouble_008",
        "category": "practical_troubleshooting",
        "turns": [
            "我的电脑接上外接显示器后偶尔会闪一下黑屏。",
            "我不是要完整诊断树。",
            "你先说最值得先排查的一件事。",
            "别讲成整套。",
        ],
    },
    {
        "case_id": "zh50_trouble_009",
        "category": "practical_troubleshooting",
        "turns": [
            "我最近视频会议的时候麦克风会忽大忽小。",
            "不要给我完整音频调校指南。",
            "只告诉我先确认什么。",
            "尽量短一点。",
        ],
    },
    {
        "case_id": "zh50_trouble_010",
        "category": "practical_troubleshooting",
        "turns": [
            "我的平板最近突然掉电特别快。",
            "我不需要完整保养手册。",
            "先告诉我第一步查什么。",
            "别补太多旁支建议。",
        ],
    },
    {
        "case_id": "zh50_trouble_011",
        "category": "practical_troubleshooting",
        "turns": [
            "我电脑最近复制大文件的时候总是卡一下。",
            "不用给我一套系统排障课。",
            "你只说先检查哪个方向。",
            "不要铺满。",
        ],
    },
    {
        "case_id": "zh50_trouble_012",
        "category": "practical_troubleshooting",
        "turns": [
            "我键盘有一个键最近经常按下去没反应。",
            "我不是要你给所有可能原因排名。",
            "先说我最先该确认什么。",
            "简洁就行。",
        ],
    },
]


def main() -> None:
    out_path = Path("directional_control_research/mechanism_experiment/outputs/heldout_eval_zh_50_v1.json")
    out_path.write_text(json.dumps(CASES, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {len(CASES)} cases to {out_path}")


if __name__ == "__main__":
    main()
