# External Multi-Axis Eval V4

这轮 `v4` 不再新增轴，只扩 `caveat / next_step / moralizing` 的 case。

目标不是简单增加样本数，而是让后续结果真的能回答两个问题：

1. 这些轴是否属于同一簇“宁多勿少”的后训练残留倾向；
2. 这些现象是否在更 axis-native 的 case 上稳定存在，而不是只靠少数特定 prompt 触发。

## 设计原则

### 1. 同簇可比较

新 case 故意让三条轴部分重叠：

- `caveat + next_step`
- `moralizing + next_step`
- `moralizing + caveat`

这样后续如果同一模型在同一类场景里：

- 既很难去掉额外 caveat，
- 又很难停止多给一步，
- 还会残留规范性 framing，

才有资格说这些轴更像同一簇，而不是互不相关的零散现象。

### 2. 负向模式必须可判读

每个 case 都明确限制：

- 不要完整指南
- 只给当前判断
- 如果要补 caveat 或下一步，只补一个
- 不要顺手写成长篇说教

这样后续即使模型输出更长，也可以区分：

- 只是稍微展开了一点；
- 还是确实顶着用户约束继续保留默认倾向。

### 3. 避免“天然就该补很多”的 case

这轮刻意不选：

- 强安全高风险医疗 case
- 必须多轮澄清才能推进的 case
- 明显需要长流程说明的 case

否则无法判断 residual caveat / next-step / moralizing 是模型 tendency，还是任务本身真的要求它这样回答。

## 新增场景

### `caveat + next_step`

- `used_laptop_seller_001`
- `rental_deposit_001`
- `subscription_cancel_001`
- `package_delay_refund_001`

这几条都是“当前判断 + 最多一条提醒/下一步”型场景。

### `moralizing + next_step`

- `roommate_dirty_dishes_001`
- `apology_text_after_argument_001`
- `team_credit_followup_001`

这几条用于看模型是否会把任务回答拖成关系维护、做人道理、规范性 framing。

### `moralizing + caveat`

- `friend_borrow_money_001`
- `coworker_punch_in_001`

这条用来测一个更典型的“既容易补 caution，又容易上价值判断”的社会性决策场景。

## 跑之前的自审结论

这批 case 现在可以支持以下判断：

- `caveat` 是否稳定残留，而不是只在单个安全类场景里发生；
- `next_step` 是否和 `caveat` 同时残留，从而更像同一簇；
- `moralizing` 的 plain-task 负向模式是否也会出现 residual framing；
- 这些现象是否跨 practical / social / workplace 三类场景存在。

但它还不能回答：

- safety-bounded 轴是否与 assistant-policy 轴共享同一机制；
- capability-bounded 轴是否会出现类似 pattern。

所以 `v4` 仍然只服务当前主论文最相关的簇判别，不扩到 `rudeness / insult / coherence`。

## 本轮建议实际测试顺序

1. 先 merge 到现有 benchmark。
2. 只跑：
   - `caveat`
   - `next_step`
   - `moralizing`
3. 先用本地 `qwen` 冒烟。
4. 再对 `deepseek_v4_flash` 提交一次 batch。
5. 结果回来后继续做 obedience-style 标注。
