# External Multi-Axis Controllability Eval v5

`v5` 的目标很窄：不给主 benchmark 再加一堆新故事，只补两条之前在 compact controlled-family 里比较脆的高层方向：

1. `clarify_first / answer_first`
2. `deferential_uncertain / decisive_direct`（在 benchmark 里继续沿用 `stance` 轴）

## 为什么要补这两条

前面的结果已经说明：

- `caveat / completeness`
- `next_step / proactivity`
- 较弱一些的 `moralizing / plain_task_frame`

这些更像一簇 `too-much assistant` 倾向。

但这还不能解释另一类问题：

- `clarify` 和 `stance` 这些方向在我们自己的 compact family 里为什么学不稳？
- 是因为这些方向在真实强模型里本来就不 sticky？
- 还是因为我们原来的 family target 没抓住它们？

`v5` 就是为这个判别服务的。

## 设计原则

### 1. clarify case 要“真的存在一个关键缺口”

如果 case 本身根本不需要澄清，那么 `ask_clarify_first` 的失败就没信息量。

因此这一组 case 只保留两类：

- 先问一个关键问题比直接给方案更合理的情境
- 或至少“先给 provisional answer”与“先问一个 key question”都说得通的情境

这样后面才能判断：

- 模型是不是天然更偏 answer-first
- 还是其实能被 prompt 切到 clarify-first

### 2. stance case 要“真的需要一个 bounded judgment”

如果 case 太开放，模型天然就会两边都讲一遍，那 `stance` 很容易退化成长度差或泛泛权衡。

因此这一组 case 都要求：

- 用户只要一个当前判断
- 不要完整方案
- 不要把两边都铺太开

这样后面才能判断：

- 模型能否被拉向更 decisively direct 的答法
- 还是会默认保留、模糊、平衡

### 3. 仍然避免纯长度判断

`v5` 不应该靠“更长/更短”来判。

真正的判读标准是：

- `clarify`
  - 是否真的先问了一个关键问题
  - 或是否在用户要求 answer-first 时仍忍不住先问
- `stance`
  - 是否真的给了相对明确的当前判断
  - 或是否在要求直接判断时仍保留大量 hedging / balancing

## 新增 case 结构

### clarify-native

- `clarify_pill_schedule_001`
- `clarify_rent_contract_001`
- `clarify_manager_reply_001`
- `clarify_travel_booking_001`

这些 case 共同点是：

- 都有一个明显但不一定致命的信息缺口
- 都能自然支持 `clarify-first` 和 `answer-first provisional guidance` 两种策略
- 不会太强地绑到 `next_step` 或 `caveat`

### stance-native

- `stance_offer_deadline_001`
- `stance_exam_signup_001`
- `stance_buy_used_phone_001`
- `stance_team_conflict_001`

这些 case 共同点是：

- 用户明确只要当前判断
- 不需要完整规划
- 适合区分：
  - `hedged / cautious / balanced`
  - `decisive / direct / commit to one side`

## 跑完后想回答什么

如果外部模型上：

- `clarify` 也很容易受控  
  那更支持：这条轴在真实模型里本来就不是强 sticky direction。

- `stance` 也很容易受控  
  那更支持：它在 compact family 里学不稳，不是偶然。

- 其中某条轴在外部模型上反而出现明显 residual tendency  
  那就支持：family 脆不等于轴本身弱，问题可能在 target construction。

## 和主论文的关系

`v5` 不是为了把 `clarify` 或 `stance` 立刻升格成主论文第二主线。

它的作用更像一个解释型补丁：

- 为什么有些高层 family 很脆
- 这些脆线在真实强模型里到底是“本来就弱”，还是“只是 family 没搭好”

如果 `v5` 结果显示它们整体都容易受控，那主论文就更有底气把重点继续收在：

- `anti_underanswer`
- `caveat`
- `next_step`
- `moralizing`

这一簇 `too-much assistant` 方向上。
