# 论文结构与写作计划

这份文档不是论文正文，而是论文写作蓝图。

它要回答的是：

- 整篇论文每一部分要完成什么任务
- 每一部分该写什么
- 哪些内容该进主文，哪些应该进 appendix
- 怎样把现有证据组织成一篇收束得当、不过度宣称的论文

---

## 0. 论文定位

这篇论文最合适的定位是：

**一篇关于 post-trained assistant policy 中 boundary-suppressibility asymmetry 的 behavioral-mechanism paper**

它不应该被写成：

- 泛泛的“模型太啰嗦”论文
- 纯 prompt engineering 论文
- 纯 circuit interpretability 论文
- 广义的 RLHF 宇宙定理

整篇论文的身份要始终保持收束。

---

## 1. 标题与定位语

## 标题该强调什么

标题最好强调：

- post-training assistant policy
- boundary-suppressibility asymmetry
- over-expansion / anti-underanswer
- user-side controllability failure

适合出现的词：

- `boundary-suppressibility`
- `assistant-policy`
- `post-training`
- `over-expansion`
- `controllability`

不适合出现的词：

- `universal`
- `all post-training`
- `causal proof`

---

## 2. 摘要怎么写

## 摘要的任务

摘要必须快速完成四件事：

1. 把问题定义清楚  
2. 说明为什么重要  
3. 概括核心证据链  
4. 给出最终收紧后的解释

## 建议结构

### 第一段：问题

说明：

- assistant 模型常被训练成避免 under-answering
- 但用户在后续交互里经常需要它收住、只答最小充分内容
- 这种“往外推”与“往回拉”的关系不是对称的

### 第二段：主现象

说明：

- `anti_underanswer` 比 `baseline` 更难压
- `minimal_boundary` 更容易保持窄边界

### 第三段：机制结果

说明：

- 这个现象不能被纯 EOS、纯 uncertainty、纯局部 continue bias 解释
- 我们系统测试过一组竞争性解释：EOS/stopping、uncertainty-compensation、planning/content budgeting、post-training assistant-policy prior、sparse branch-point supervision
- retained evidence 更支持一个 mixed planning/stopping 问题，并指向 bundled assistant-policy bias

### 第四段：阶段与泛化

说明：

- later anti-oriented SFT 可以继续放大
- cleaner preference-like reversal 可以把 anti 拉回，但这种 reversal capacity 不对称
- 第二家族方向性复现成立

### 最后一句

用一句话收成：

- 这不是 generic verbosity，而是一个相对特殊的 post-training controllability 现象

## 摘要里不要做的事

- 不要塞太多 run 名
- 不要把所有实验名全列出来
- 不要做 universality overclaim

---

## 3. 引言怎么写

## 引言的任务

引言要把读者从：

- “这不就是长一点吗”

带到：

- “这是一个真实的 post-training controllability 问题，而且有机制意义”

## 推荐结构

### 3.1 开场问题

开场先讲 assistant policy tension：

- 训练阶段往往奖励“不答少”
- 真实使用里用户却经常要求“只答当前问题、别多给”
- 这两种压力不是对称的

### 3.2 为什么这个问题不 trivial

这里必须写清楚：

- 问题不是“模型会不会说长”
- 也不是 generic helpfulness
- 真正重要的是：当用户明确要求短答、收边界、不要多给时，模型为什么压不回去

要明确点出前期探索逼出来的关键事实：

- 当用户要求“不要反问”“不要额外提供帮助”时，模型常常能遵守
- 真正更难压的是“回答短一点”“只答最小充分内容”“不要继续展开”

也就是说：

- 问题不是 generic verbosity
- 而是一个沿着回答长短 / scope breadth 轴集中的 controllability failure

### 3.3 这个问题是怎么收敛出来的

这一段放在引言里，而不是拖到 setup 才讲。

要高层回顾：

- 最开始研究的是更 general 的 directional control / assistant behavior control
- 做过 prompt-side taxonomy、mixed discovery、probe risk、chat-vs-base 粗对照
- 一路排除之后，问题才收缩成 boundary-suppressibility asymmetry

这一段的作用是：

- 说明问题不是事后挑出来的
- 说明这不是 trivial observation
- 给后面的 controlled family 提供研究动机

### 3.4 本文做了什么

高层概括方法：

- controlled SFT family
- mechanism probes
- stage split
- cleaner reversal
- second-family directional replication

### 3.5 本文贡献

建议最后用 3--5 个短贡献 bullet：

- 把研究对象从 generic verbosity 收缩成 boundary-suppressibility asymmetry
- 建立 controlled assistant-policy family
- 通过多 probe 把机制收束成 mixed planning/stopping bundled bias
- 给出 same-direction amplification 与 asymmetric reversal 证据

## 引言里不要做的事

- 不要一开始就讲太多 related work
- 不要过早堆细节 run name

---

## 4. 问题设置 / 实验框架怎么写

这一节可以叫：

- `Problem Setup`
- `Experimental Framing`
- `Controlled Policy Setup`

## 要写什么

### 4.1 三个主 family 是什么

- `baseline`
- `anti_underanswer`
- `minimal_boundary`

把它们写成 assistant-policy target，而不是“训了三个模型”。

### 4.2 triplet 设计为什么重要

强调：

- 同一个 `user_text`
- 三个 target answer
- 同一个 base model
- 同一个 SFT pipeline

这样比较的是 policy direction，而不是不同任务分布。

### 4.3 主评测到底在测什么

明确说：

- 不是默认长度
- 而是用户显式要求收缩时，模型还能不能被拉回去

### 4.4 retained evidence 的规则

最好在这一节就提前说：

- 本文区分 retained / partial / exploratory / excluded evidence

这会让 reviewer 更信你没有选择性汇报。

---

## 5. 主现象结果怎么写

这是第一节真正的结果段落。

## 要写什么

### 5.1 Phase 2 主边界评测

展示：

- `baseline`
- `anti`
- `minimal`

核心结论：

- anti hardest to suppress
- minimal easiest to keep narrow

### 5.2 为什么这不是普通“更长”

明确强调：

- 研究对象是 suppressibility
- 不是 raw verbosity

### 5.3 可选：base 对照

可以简短放：

- raw base 更 continuation-prone

但这部分不要太重，避免抢主线。

## 需要什么表

至少一张主表：

- family × boundary mode
- 主长度指标
- 可加一个 secondary controllability 指标

---

## 6. 机制拆解怎么写

这是整篇论文的核心科学部分。

最好的写法不是 probe 列表，而是**一条逐步收束的论证链**。

## 推荐顺序

### 6.1 先排除浅解释

这里放：

- `prefix50 / true_eos / tailspan`
- uncertainty probe
- branchpoint probe

这一小节的作用是先说明：

- 不是纯 EOS
- 不是纯 uncertainty
- 不是纯局部 continue bias

### 6.2 再证明这是 mixed planning/stopping 问题

这里放：

- `same_information_compression`
- `true_pruning`
- planning-vs-stopping 标注
- forced-prefix continuation

这一小节的作用是说明：

- 前段有 planning / content-budgeting overshoot
- 后段有 continuation / stopping persistence
- 而且不同 mode 暴露不同 mixture

### 6.3 最后再收成 bundled assistant-policy bias

这里放：

- asymmetric controllability
- bundled generalization

这一小节的作用是说明：

- 现象不是孤立的长度偏移
- 而是和 planning、stopping、额外帮助、clarify tendency 一起联动的高层 policy bundle

---

## 7. Stage split 与 reversal 怎么写

这一节回答：

- 这种 asymmetry 在训练流程哪一层出现
- 哪一层会放大
- 哪一层能拉回

这节必须明确强弱分层，不要把所有结果并排。

## 推荐顺序

### 7.1 同向放大：SFT 比 preference 更强

先写：

- `baseline_then_anti_stage2_v1`
- `baseline_then_preference_expand_*`

结论：

- later anti-oriented SFT 是当前最强放大器
- preference-like same-direction amplification 真实存在，但更弱、且 non-monotonic

### 7.2 反向改写：只有 anti side 有强 retained reversal

重点写：

- `anti -> preference_minimal v2`

明确：

- 这是 cleaner retained reversal 主证据
- 不只是变短，还把 bundled expansion tendency 压平
- 但更像 pullback to narrow regime，不是恢复出完美灵活 controllability

### 7.3 minimal side：只有 partial midpoint pullback，而且更脆

这里再写：

- `minimal -> preference_baseline ... v2`
- minimal-side tiny sweep

结论：

- midpoint pullback 部分成立
- 但明显更弱、更脆
- 因而 reversal capacity 是不对称的

### 7.4 不要写什么

明确写边界：

- 没有对称 clean reversal
- 没有证明 later preference can rewrite any policy

---

## 8. 外部效度怎么写

这节要短，不要展开成 model zoo。

## 写什么

### 8.1 SmolLM2

- cross-family
- cross-language
- directional replication

### 8.2 边界

- 不是同语言同任务数值复刻
- 但足以支持方向性泛化

## 不写什么

- 不要详写所有失败的 second-family 救火史

那些放 appendix 或 excluded table。

---

## 9. 额外高层方向怎么写

这节要短，而且非常谨慎。

## 写什么

### 9.1 为什么要试

- 想测试 anti-underanswer 是否只是 arbitrary high-level axis

### 9.2 试了什么

- `affect_attuned vs affect_flat`
- `deferential_uncertain vs decisive_direct`

### 9.3 发生了什么

- 训练和 smoke 都能跑
- fuller eval 没形成 retained clean axis

### 9.4 安全解释

- 这不证明 over-expansion 是唯一 sticky 方向
- 但支持：
  - 在当前 framework 里，anti-underanswer 是 comparatively privileged
  - 不是所有高层方向都同样容易被稳定固化、同样容易形成 clean suppressibility asymmetry

## 不要写什么

- 不要把这两条写成“严格负证明”

---

## 10. Discussion 怎么写

这一节不要写成泛泛的 alignment 口号，而要专门解释：

- 为什么这不是 trivial 的长度现象
- 为什么这条轴显得相对特殊
- 我们现在到底能说到什么程度

## 建议讨论点

### 10.1 为什么 anti-underanswer 比较特殊

不要写成“因为它更容易学到，所以它特殊”，那不够解释，也容易被 reviewer 追问“是不是其它轴没做对”。

更好的写法是：

- 现有证据表明，over-expansion 不是任意高层方向的一个普通例子
- 与浅层特征相比：
  - 像 `emoji_only` 这样的表层风格很好被用户后续指令压下去
- 与其它高层探索相比：
  - affect / stance 没有形成同等级别的 clean retained axis
  - minimal-side midpoint pullback 也明显更脆
- 与 generic helpfulness 假说相比：
  - 模型并不是对所有“别额外帮助/别追问”的要求都压不住
  - 真正特殊的是“短答 / 收边界 / 别展开”这条轴

最后再谨慎提出解释边界：

- 这些结果更一致地指向一种 comparatively privileged expansion tendency
- 它可能与更深的 continuation prior 或 pretraining-era bias 有关
- 但本文不能把这一点写成已被完全证明的因果来源

### 10.2 bundled-policy 语言在这里的作用

这一小节要明显收缩，不要写成泛泛理论。

只需要说明：

- 我们保留 bundled-policy 语言，不是因为它新奇，而是因为它最贴合 retained evidence
- 也就是说：
  - 现象不是单独的长度偏移
  - 而是与 planning、stopping、额外帮助、clarify tendency 一起联动

一句话够了，不需要展开成长讨论。

---

## 11. Limitations 怎么写

这节必须主动、清楚、诚实。

## 必写限制

1. case manifold 较紧
- 很多训练线来自小 canonical pool + wrapper 扩展

2. 没有 circuit-level evidence
- 这是 behavioral-mechanism paper

3. 外部效度是方向性的
- 只有一条 retained second-family line

4. 额外高层方向没有形成 retained clean axis
- generality 仍然有边界

5. reversal 是不对称的
- 没有 symmetric rewrite story

6. 一些 exploratory line 被排除
- 要有 retained/excluded table

---

## 12. 结论怎么写

结论要短，收束，不拔高。

## 建议内容

1. 再说一遍现象
- anti-underanswer 更难压

2. 再说一遍机制解释
- mixed planning + stopping
- bundled assistant-policy bias

3. 再说一遍 stage 结果
- SFT 内部能放大
- later preference-like reversal 存在但不对称

4. 再说一遍 comparative specialness
- anti-underanswer 在当前框架里是 comparatively privileged

## 不要写什么

- 不要 universalize
- 不要写成“我们彻底解决了这个机制”

---

## 13. Appendix 该放什么

Appendix 要承接主文不该堆的东西。

## 推荐内容

### A. Dataset / triplet construction

- triplet 数据生成
- wrappers
- categories

### B. Probe specs

- Phase 2 mode wording
- forced-prefix cases
- asymmetric / bundled spec

### C. Retained vs excluded evidence table

- line
- status
- exclusion reason

### D. 更多 sample

- representative good
- representative bad / excluded

### E. 实现审计摘要

- 修过的问题
- 修后哪些结论仍然有效

---

## 14. 正文里的四个主 claim

正文不要让读者感觉有十个并列发现。

正文层面只保留四个主 claim：

1. 主现象：
- anti-underanswer hardest to suppress under explicit boundary instructions

2. 机制：
- 不是浅解释，而是 mixed planning/stopping bundled bias

3. 阶段：
- SFT 内部可放大；later preference-like reversal 真实存在且不对称

4. 边界：
- 这是一个 comparatively privileged direction，不是 arbitrary high-level axis 的普通例子

其它 claim 都作为 supporting subclaims 服务这四条。

---

## 15. 实际写作纪律

- 主文只讲 retained evidence 和必要的 weaker partial evidence
- exploratory negative evidence 要短写
- excluded lines 放表或 appendix
- run name 不要在主文泛滥
- 如果一段像 changelog，就压缩

---

## 16. 接下来的具体写作任务

下一步最该产出的东西是：

1. 主表和结果表骨架
2. `Introduction` 初稿
3. `Problem Setup / Main Results / Mechanism` 初稿
4. retained / excluded evidence table

这份文档应该作为整篇论文的 section-by-section 控制蓝图使用。
