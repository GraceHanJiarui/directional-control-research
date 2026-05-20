# External Multi-Axis Controllability Eval v2

这份 `v2` 不是推翻 `v1`，而是在 `v1` 基础上补两个缺口：

1. 让 case 更 axis-native，减少“这个 case 本来就不适合测该轴”的争议；
2. 增加两个更高层、但不那么直接贴着长度轴的方向。

## 为什么需要 v2

`v1` 已经给出一个重要结论：

- controllability cost 不是均匀分布在所有轴上的；
- `format` 很容易控；
- `scope` 在外部强模型上并不总是最顽固；
- `caveat` 和 `next_step` 更像真正有 tension 的方向。

但 `v1` 还有两个明显不足：

1. 现有最有张力的轴，还是与“宁多勿少”的展开倾向相邻；
2. 还缺少足够高层、又不是纯长度变体的轴来判断：
   - 后训练代价是否只集中在长度/完整性一簇；
   - 还是也会出现在别的高层方向。

## v2 新增的两个轴

### 1. `stance`
- `ask_hedged_cautious`
- `ask_decisive_direct`

这个轴测的是：
- 模型是否会保留更谨慎、更多保留条件的判断风格；
- 以及用户要求它更果断时，是否能真的切过去。

这条轴比 `scope` 更少受“回答长短”本身影响，
但又很像后训练会鼓励的高层行为：
- 审慎
- 不过度承诺
- 减少误导

### 2. `optionality`
- `ask_offer_two_options`
- `ask_single_recommendation`

这个轴测的是：
- 模型是否倾向于把回答扩成多个平衡选项；
- 用户要求“只给一个你认为最合适的建议”时，它能否收住。

这条轴很有价值，因为它碰到的不是纯长度，
而是 assistant 常见的：
- broaden the answer
- hedge commitment
- avoid taking one hard stance

## v2 新增 case 的设计原则

新增 case 都尽量满足：

- 不要求完整方案；
- 允许存在一个小而直接的判断；
- 但也天然会诱发：
  - option broadening
  - cautious stance
  - one-more-step help
  - extra caveat

新增 case 见：
- `directional_control_research/data/external_multi_axis_controllability_v2_patch.json`

代表性的新增 case：

- `purchase_laptop_wait_001`
- `task_resume_edit_001`
- `travel_daytrip_weather_001`
- `task_meeting_reply_001`
- `finance_subscriptions_001`
- `social_reply_delay_001`

## 推荐执行顺序

1. 先保留 `v1` 的人工 obedience-style 标注结论；
2. 再把 `v2_patch` merge 到 `v1` spec；
3. 优先在外部强模型上跑新增轴：
   - `stance`
   - `optionality`
4. 再看它们是否也出现类似：
   - residual cautiousness
   - residual option-broadening
   - user-side suppression weakness

## 这一步想回答什么

如果 `stance` 和 `optionality` 也出现明显 tension，
那会支持：

- 后训练代价并不只集中在长度相关轴；
- 它更可能集中在一簇更高层的 assistant virtues：
  - cautiousness
  - completeness
  - option broadening
  - proactivity

如果这两条轴没有形成类似 tension，
那会更支持：

- 当前最特殊的仍是“宁多勿少”这一簇方向；
- 长度/完整性相关方向确实比较 privileged。
