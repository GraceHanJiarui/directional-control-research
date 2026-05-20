# 外部强模型 Multi-Axis Controllability Eval 方案

这套方案的目标不是解释训练机制，而是先在**现成强模型**上回答一个更上游的问题：

- 现成后训练助手在多个高层轴上，是否都会出现类似的 user-side controllability weakness；
- 还是说 short-answer / scope-breadth 轴比较特殊。

这套 benchmark 刻意不依赖自训 family，也不依赖额外 adapter。它只测试：

- 同一个模型；
- 同一条 case；
- 一对正反 mode；
- 模型到底能不能切过去。

---

## 设计原则

### 1. 轴要尽量贴近现成 assistant 的真实后训练偏向
这次不选过于薄、过于 persona 化的轴。

优先选的是：
- short-answer / scope-minimal
- add-one-next-step / no-next-step
- more-complete-caveat / no-extra-caveat
- clarify-first / answer-first
- bullet-points / plain-text
- warm-supportive / neutral-transactional

这些轴里，前四条更像现代 assistant 真正会被鼓励的行为倾向；
后两条分别承担：
- 一个浅表格式对照；
- 一个中层 interpersonal style 对照。

### 2. 每条轴都要有显式的反向控制
不是只测：
- “模型会不会更主动”

而是测：
- 用户明确要求它不要更主动时，它还能不能收回来。

### 3. 第一轮不做复杂自动判分
第一轮先保留：
- 原始输出；
- 长度；
- per-axis/per-mode 汇总；
- 后续可以再补人工标注或弱规则标注。

---

## 六条轴

### A. `short_answer` vs `scope_minimal`
问题：
- 用户要求最小充分回答时，模型是否仍会不必要地继续展开。

### B. `add_one_next_step` vs `no_next_step`
问题：
- 模型是否会在用户不要推进时，仍然额外给下一步建议。

### C. `more_complete_caveat` vs `no_extra_caveat`
问题：
- 模型是否会在用户不想听额外 caveat 时，仍习惯性补风险、限制、提醒。

### D. `clarify_first` vs `answer_first`
问题：
- 模型是否会在能直接答的时候，仍然偏向先追问一个澄清问题。

### E. `bullet_points` vs `plain_text`
问题：
- 浅表格式轴是否显著更容易被 prompt 精确控制。

### F. `warm_supportive` vs `neutral_transactional`
问题：
- 中层 interpersonal style 是否比长度轴更容易受控，还是也会出现难以压回的现象。

---

## 推荐先测模型

第一轮建议只跑少量强模型：

1. 一个 OpenAI 强模型
2. 一个 DeepSeek chat / instruct 模型
3. 一个其它开源 instruct 模型

如果只跑两类，也足够：
- GPT 系列
- DeepSeek 系列

---

## 输出文件结构

`run_external_multi_axis_eval.py` 输出逐条 JSONL，包含：
- `model_name`
- `case_id`
- `axis_id`
- `mode_key`
- `assistant_text`
- `char_length`
- `elapsed_s`
- `raw_response`

`summarize_external_multi_axis_eval.py` 先做轻汇总：
- per model / axis / mode 的样本数
- 平均长度
- 中位长度

这一步不自动判“服从了没有”，因为不同轴的失败模式不同。

---

## 这套方案能回答什么

如果跑完后看到：

### 情况 1
只有 `short_answer / scope_minimal` 一直很难压

那更支持：
- 这条轴相对特殊；
- 不只是 generic post-training obedience 问题。

### 情况 2
`next_step`、`caveat`、`clarify` 这些轴也明显难压

那更支持：
- 后训练可能更一般地损伤了用户在多个高层轴上的 controllability。

### 情况 3
浅表 `bullet_points` 很好控，高层轴里只有部分难控

那会形成很有信息量的层级图：
- shallow formatting
- mid-level interaction
- high-level scope / completeness

并能更清楚地区分：
- surface obedience
- high-level controllability

---

## 当前边界

这套 benchmark：
- 不解释训练机制；
- 不告诉我们 SFT 和 DPO 各自怎么造成这些现象；
- 也不直接给出 causal claim。

它的作用是：
- 给出现成强模型上的外部现象分布；
- 帮我们判断 short-answer / scope 轴是否真的更特殊；
- 决定后面是否值得对其它轴继续做自训 family。
