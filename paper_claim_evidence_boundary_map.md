# 论文 Claim / Evidence / Boundary Map

这份文档是整篇论文的总控表。

它的作用是把下面几件事明确分开：

- 哪些结论可以强写
- 每个结论分别由哪些证据支持
- 每个结论必须带着哪些边界一起写
- 哪些话现在不能写

---

## 0. 论文核心问题

这篇论文研究的不是泛泛的“模型会不会啰嗦”，而是一个更具体的问题：

**为什么一种 anti-underanswer / 过度展开导向的 assistant policy，在用户明确要求收缩边界时，会变得难以压回去？这种 stickiness 背后的机制是什么？**

核心现象是：

- `anti_underanswer` 在显式 boundary instruction 下更难压回去
- `minimal_boundary` 更容易保持窄边界
- 这种差异跨多个 probe 重复出现

---

## 1. 可以强写的主结论

## Claim 1

**在显式用户侧边界指令下，`anti_underanswer` 比 `baseline` 更难被压回，而 `minimal_boundary` 更容易保持收缩。**

### 证据

- 中文 Qwen 主线：
  - `baseline_sft_v5`
  - `anti_underanswer_sft_v5`
  - `minimal_boundary_sft_v5`
- 主边界评测（Phase 2）：
  - `avoid_underanswer`
  - `scope_minimal_sufficient`
  - `do_not_add_unasked_help`
- 反复人工 sample 检查

### 为什么这条可以强写

- 同一个 base model
- 同一套训练流程
- 同一批任务分布
- 只改变 assistant-policy target

### 必须带的边界

- 这是一个行为层面的 suppressibility claim，不是完整机制解释本身
- 不能只拿“长度”一个数来讲，必须和后续 probe 一起读

### 现在不能写成什么

- 不能写成“anti 永远更长”
- 不能把它降格成一个普通 verbosity 现象

---

## Claim 2

**当前 retained evidence 支持一个 mixed mechanism：anti-underanswer persistence 同时包含前段 planning/content-budgeting overshoot 和后段 continuation/stopping persistence。**

### 证据

1. `planning-vs-stopping` 定量标注 (`v2`)
- `80` 条标注
- 总体：
  - `planning_overshoot = 0.338`
  - `stopping_failure = 0.662`
- 按 mode：
  - `scope_minimal_sufficient` 更偏 planning
  - `do_not_add_unasked_help` 更偏 stopping
- 按模型：
  - `baseline_then_anti_stage2` 在两者上都最差

2. compression vs pruning
- `anti_underanswer` 在 `same_information_compression` 下经常更糟
- `true_pruning` 能拉回一些，但仍明显高于 baseline

3. forced-prefix continuation
- `anti` 在最小充分前缀之后更容易继续补

### 为什么这条可以强写

- 人工标注、probe、stage 结果相互收敛
- 不是依赖单一指标

### 必须带的边界

- 这是功能层面的机制拆解，不是内部电路解释
- `planning / stopping` 是行为分类，不是直接观察到的 latent module

### 现在不能写成什么

- 不能写成“已经把 planning 和 stopping 对应到两个明确内部模块”

---

## Claim 3

**这个现象不能被“纯 EOS 失败”“纯 uncertainty-compensation”“纯局部 one-step continue preference”“纯 wording compression failure”这些简单解释充分说明。**

### 证据

1. EOS / tail supervision 线
- `anti_prefix50`
- `anti_prefix50_plus_true_eos_v2`
- `anti_prefix50_plus_tailspan_v3`
- 结果：
  - EOS 有帮助
  - continuous tail span 更有帮助

2. uncertainty probe
- entropy / top1-top2 margin / first-token 指标
- 很多长 anti 输出并不更不确定，反而更 confident

3. branchpoint probe
- 不支持“主要就是局部 continue preference”这种简单解释

4. compression vs pruning
- `same_information_compression` 常常让 anti 更糟
- `true_pruning` 更有效，说明更像内容选择问题而不是措辞压缩问题

### 为什么这条可以强写

- 这些 probe 对替代解释起的是直接约束作用

### 必须带的边界

- 这些证据削弱的是这些假说的“简单版”
- 不等于这些因素完全没有作用

### 现在不能写成什么

- 不能写成“EOS 完全无关”
- 不能写成“不确定性绝对没有作用”

---

## Claim 4

**一个后续 anti-oriented SFT stage 可以在 SFT 内部继续放大这种 asymmetry。**

### 证据

- `baseline_then_anti_stage2_v1`
- 在 suppressive Phase 2 mode 下仍明显更展开
- forced-prefix continuation 更强
- controllability 更失衡

### 为什么这条可以强写

- 这是干净的 stage split：
  - stage 1：`baseline_sft_v5`
  - stage 2：继续在 anti-underanswer target 上训练

### 必须带的边界

- 对称的 `baseline_then_minimal_stage2_v1` 不稳定，不能用
- 所以这条 stage 证据目前是单侧更强

### 现在不能写成什么

- 不能写成“所有 later SFT stage 都会这样”

---

## Claim 5

**后续 preference-like optimization 也可以重塑 policy；其中一条强 retained reversal 结果表明，它确实能把一个已经 sticky 的 anti policy 拉回到 narrow regime。**

### 证据

1. same-direction preference amplification
- `baseline_then_preference_expand_stage3_gpu_medium_v1`
- `baseline_then_preference_expand_stage3_gpu_large_stable_v1`

2. cleaner reversal
- retained：
  - `anti_then_preference_minimal_stage3_gpu_large_stable_v2`
- 关键指标：
  - Phase 2 均值约 `12-15`
  - forced-prefix `9/12` 立即停
  - mean continuation `1.0`

3. 对 retained reversal 的 bundled eval
- bundled expansion tendency 基本被压平

### 为什么这条可以强写

- cleaner `v2` rebuild 修掉了三类关键混淆：
  - pair anchor 不一致
  - broken minimal-side pair construction
  - Windows JSON DPO loader 不稳定

### 必须带的边界

- 这条支持的是强 anti-side pullback
- 不支持“later preference 可以对称地重写任何已有 policy”

### 现在不能写成什么

- 不能写成“later preference stage 一般都能 undo 任意 SFT policy”

---

## Claim 6

**preference-like reversal capacity 在 policy 两侧是不对称的。**

### 证据

1. 强 anti-side pullback
- `anti -> preference_minimal v2`

2. 弱一些的 minimal-side pullback
- retained 但更弱：
  - `minimal_then_preference_baseline_task_primary_minanchor_stage3_gpu_medium_v2`
- 只是 partial midpoint pullback

3. minimal-side tiny sweep
- 两条 tiny sweep 都塌成 `!!!!...`
- 支持的是 brittleness，不是更干净的 midpoint recovery

### 为什么这条可以强写

- 同一套 cleaner rebuild family
- 同一条 DPO 训练链路
- 同一类数据清理原则
- 结果仍然是明显不对称

### 必须带的边界

- 这条最强的是 comparative claim
- 不等于 minimal-side reversal 在原理上永远不可能成功

### 现在不能写成什么

- 不能写成“minimal side 永远拉不回来”

---

## Claim 7

**当前最好的机制图景是 bundled assistant-policy bias，而不是单个浅层行为特征。**

### 证据

1. asymmetric controllability
- 主线 family 的响应结构不是简单一维旋钮

2. eval-only bundled generalization
- `baseline` 较平
- `minimal` 较温和、较对称
- `anti` 更失衡
- `baseline_then_anti_stage2` 更失衡

3. compression/pruning + forced-prefix
- 说明多个相邻决策倾向会一起移动

### 为什么这条可以强写

- 这条解释同时解释了：
  - 为什么 shallow style 很容易学
  - 为什么高层 single-axis family 很难做干净

### 必须带的边界

- 这里的 “bundled” 是行为/训练层面的描述
- 还不是 representation-level decomposition

### 现在不能写成什么

- 不能写成“我们已经找到了一个单独的 latent variable”

---

## Claim 8

**核心方向性现象在原始 Qwen 中文主线之外也能复现。**

### 证据

- SmolLM2 英文 second-family line：
  - `HuggingFaceTB/SmolLM2-1.7B-Instruct`
- directional replication：
  - `anti` 在 suppressive mode 下仍更难压
  - forced-prefix continuation 更强
  - bundled/asymmetric control picture 仍存在

### 为什么这条可以强写

- 这条外部线是可运行、可评测、可解释的
- 不是只有 smoke

### 必须带的边界

- 这是 cross-family + cross-language directional replication
- 不是 same-language same-task same-metric reproduction

### 现在不能写成什么

- 不能写成“和 Qwen 指标完全一一对应”

---

## 2. 可以写，但强度要收紧的结论

## Claim 9

**在当前 compact stage-2 framework 下，`anti_underanswer / over-expansion` 相比我们额外尝试的其他高层方向，表现出相对特殊性。**

### 证据

- `anti_underanswer` 是当前最干净、最稳定的 retained 高层方向
- `affect_attuned vs affect_flat` 没形成 retained clean axis
- `deferential_uncertain vs decisive_direct` 没形成 retained clean axis
- `minimal-side midpoint pullback` 比 anti-side pullback 明显更脆

### 这条的价值

- 支持一个 comparative specialness 读法
- 让主线看起来不像一个随手挑的 lucky axis

### 必须带的边界

- 这是 comparative claim，不是绝对唯一性 claim
- 不等于 over-expansion 是世界上唯一会 sticky 的高层方向

### 现在不能写成什么

- 不能写成“所有其他高层方向都不会 sticky”

---

## Claim 10

**额外的高层方向确实被认真尝试过，但在当前框架里没有形成和 anti-underanswer 同级别的 retained evidence。**

### 证据

- `affect` 线多轮 rebuild：
  - `v1`
  - same-content `v2`
  - emotional-case-only `v3`
- `stance` 线：
  - `deferential_uncertain vs decisive_direct`
- 都训练了
- 都跑了 smoke
- fuller eval 也做了

### 必须带的边界

- 这是 exploratory negative evidence
- 不能被上升成“严格不可能”

---

## 3. 现在不能写的结论

- “所有高层 assistant-policy direction 在 SFT 后都会同样 sticky”
- “over-expansion 是唯一可能 sticky 的高层方向”
- “preference optimization 可以对称地重写任意已有 SFT policy”
- “我们已经完全隔离出内部因果机制”
- “这是所有 post-training pipeline 的普遍规律”
- “SmolLM2 是和 Qwen 一一对应的复制”
- “affect / stance 证明了所有非 expansion 方向都不成立”

---

## 4. Retained / Excluded 证据清单

## Retained

- 主线 SFT family：
  - `baseline_sft_v5`
  - `anti_underanswer_sft_v5`
  - `minimal_boundary_sft_v5`
- EOS / tailspan：
  - `anti_prefix50`
  - `anti_prefix50_plus_true_eos_v2`
  - `anti_prefix50_plus_tailspan_v3`
- 主机制 probe：
  - uncertainty
  - compression-vs-pruning
  - forced-prefix
  - asymmetric controllability
  - bundled generalization
- stage split：
  - `baseline_then_anti_stage2_v1`
  - usable preference expand runs
  - `anti -> preference_minimal v2`
  - `minimal -> preference_baseline ... v2` 作为较弱 partial evidence
- planning-vs-stopping `v2`
- SmolLM2 replication

## Excluded / not retained

- old broken `one_layer`
- dirty early preference-stage v1 lines
- unstable `baseline_then_minimal_stage2_v1`
- `clarify_first_sft_v1`
- `next_step_heavy_proxy_v1`
- `proactive_bundle_proxy_v1`
- 额外高层方向：
  - affect line
  - stance line

---

## 5. 论文级总括句

如果把整篇论文压成一句最稳的话：

**难压的过度展开并不是普通 verbosity，而是一条在当前框架下相对特殊、可被 post-training 强化、同时涉及 planning 与 stopping 的 bundled assistant-policy direction；它可以被后续阶段部分逆转，但这种 reversal capacity 明显不对称。**

---

## 6. 最后的写作纪律

写论文时必须始终分清四类东西：

- retained evidence
- weaker partial evidence
- exploratory negative evidence
- excluded runs

如果一段话把这四类混在一起了，就需要重写。
