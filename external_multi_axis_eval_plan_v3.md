# External Multi-Axis Controllability Eval v3

`v3` 的目的不是立刻服务主论文的 strongest claim，而是把外部 benchmark 明确扩成三层：

1. **assistant-policy-related axes**
2. **capability-bounded axes**
3. **safety / politeness-bounded axes**

这样后面得到的负/正结果不会混着解释。

## 为什么要做 v3

到 `v2` 为止，外部 benchmark 已经支持：

- controllability cost 不是均匀分布在所有轴上；
- `caveat` 比 `format`、`clarify` 更像真实 tension 轴；
- `next_step` 也有一定 residual tendency；
- `stance` 和 `optionality` 比较弱，其中 `optionality` 有一些新信息。

但还剩一个关键空白：

- 如果只继续围绕 `scope`、`next_step`、`caveat`、`optionality` 打转，
  仍然难以区分：
  - 这是不是“宁多勿少”这一簇方向的特殊性；
  - 还是后训练更广泛地重塑了用户对高层行为的控制权。

因此 `v3` 的任务是：把外部 benchmark 明确扩到新的方向，并且把这些方向在解释上分层。

## 三层框架

### 1. assistant-policy-related axes

这组最贴近当前主论文的问题：

- `sycophancy`
  - `agree_with_user`
  - `push_back_when_needed`
- `contrarian`
  - `push_back_when_needed`
  - `reflexive_contrarian`
- `moralizing`
  - `moralizing_frame`
  - `plain_task_frame`

这些方向都不是纯长度控制，
但仍然像真实后训练可能会鼓励或抑制的高层行为倾向。

### 2. capability-bounded axes

- `coherence`
  - `coherent`
  - `intentionally_incoherent`
- `text_integrity`
  - `normal_text`
  - `scrambled_text`

这组不是主论文最核心的方向，
但它们可以帮助区分：

- assistant-policy controllability
vs
- model basic capability / readability priors

如果这组轴几乎完全压不动，
那说明有一类“反方向控制”本质上是在逼模型破坏自己的基本语言能力。

### 3. safety / politeness-bounded axes

- `submission`
  - `submissive_deferential`
  - `neutral_direct`
- `rudeness`
  - `rude_sarcastic`
  - `respectful_plain`
- `insult`
  - `insulting_hostile`
  - `respectful_plain`

这组对主论文的直接价值较低，
但对“后训练后究竟哪一层在限制 controllability”这个更一般的问题有价值。

它们可以帮助区分：
- 是 assistant-policy 倾向在起作用；
- 还是 safety / politeness guardrails 在起作用。

## 新增 case 的设计原则

新增 case 都尽量满足：

- 低风险、低 stakes，避免 case 本身触发过强安全分歧；
- 尽量把轴效应和内容效应分开；
- 对同一 case，优先测一种主要轴，避免每个 case 挂太多互相干扰的轴。

## 解释规则

`v3` 的结果不能一锅端解释。
建议后续汇总时按下面三组分别报告：

1. assistant-policy controllability
2. capability-bounded controllability
3. safety-bounded controllability

这能避免出现一种常见误读：

- “模型不愿意侮辱用户” 和
- “模型很难停止补充 caveat”

虽然都可以叫 controllability，
但它们不是同一种 controllability 现象。

## 推荐执行顺序

1. 先完成 `v1` 和 `v2` 的人工 obedience-style 标注与总结。
2. 在外部模型上先跑 `v3` 的 assistant-policy-related 轴：
   - `sycophancy`
   - `contrarian`
   - `moralizing`
3. 只有在这一步有信息量后，再决定是否继续跑：
   - `coherence`
   - `text_integrity`
   - `submission`
   - `rudeness`
   - `insult`

## 对主论文的关系

`v3` 不应直接并入主论文主结果，除非后续证据显示：

- 某条新增高层轴也出现了和 `caveat` 类似的 residual tendency；
- 并且其 failure mode 不主要由 safety 层或 capability 层解释。

如果做不到这一点，`v3` 更适合成为：

- 扩展研究计划；
- 或者新开一篇关于后训练后 controllability atlas 的论文雏形。
