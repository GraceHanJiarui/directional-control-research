# 旧外界模型 / 现成模型相关 eval 对照表

这份表专门回答一个问题：

- 我们以前在**现成模型**上到底做过哪些 eval；
- 这些线各自能回答什么；
- 为什么它们**还不能直接回答**“其它轴的 controllability 是否也会被后训练损伤”；
- 如果现在要回答这个问题，还缺什么。

这里的“现成模型”包括：
- 本地直接跑的开源 base/chat/instruct 模型；
- 早期 prompt-side directional-control eval；
- 后来用于确认主现象方向性的外部 family/语言验证。

---

## 总结版

最重要的结论先说：

1. **做过不少现成模型 eval。**
   但其中大部分回答的是：
   - prompt 能不能把某个方向拨动；
   - base vs chat / instruct 的粗粒度差别；
   - 主线边界轴在别的模型上是否还能看到。

2. **这些旧线大多没有直接测“其它轴在用户反向约束下压不压得回去”。**
   也就是说，它们更接近：
   - bendability / steerability
   - stage-level rough comparison
   而不是：
   - user-side suppressibility / controllability benchmark

3. **因此它们不能直接回答：**
   - 是不是只有 short-answer / scope 轴特别难控；
   - 还是后训练更一般地损伤了用户对其它高层轴的 controllability。

4. **现在真正缺的是：**
   - 在现成强模型上，
   - 对多个“后训练本来就会鼓励的高层轴”，
   - 直接做正向/反向 mode 的 controllability 测试。

---

## 对照表

| 线 | 代表文件 / 结果 | 模型 / 对象 | 主要测什么 | 已经回答了什么 | 为什么不能直接回答“其它轴 controllability 是否也坏” | 现在缺什么 |
|---|---|---|---|---|---|---|
| Prompt-side taxonomy pilot | `eval/paper_eval_style_control_taxonomy_pilot_v2_out/` | 早期现成 chat/instruct 运行线 | scope、proactive、warm、professional、format 等 mode 的 prompt-side 可拨动性 | 很多高层维度会动；格式类更容易控；高层维度常常一起动 | 主要看的是长度/风格响应，不是用户反向约束下能否压回；更像 bendability，不是 suppressibility | 需要把这些轴改造成显式正反向 controllability eval，而不只是 prompt taxonomy |
| Mixed discovery / probe risk | `eval/paper_eval_directional_control_mixed_discovery_12_v1_out/`, `eval/paper_eval_directional_control_probe_risk_v1_out/` | 早期现成模型 eval | 更聚焦的高层方向：最小充分、更多主动、更多风险说明、更多 warm/support | 看到很多高层方向不是单轴，而会 bundle 在一起 | 仍然主要是“会不会被 prompt 拨动”；没有形成“该轴在用户反向约束下是否顽固”的明确评测 | 需要把这些高层轴写成 paired mode，并在现成模型上直接看 obedience / suppressibility |
| DeepSeek base vs chat 粗对照 | `scripts/run_deepseek_stage_compare_direct.py`, `results/deepseek_base_chat_direct_v1.jsonl`, `runtime/local_llm/README.md` | `deepseek-base` vs `deepseek-chat` | base vs chat 在 `neutral / avoid_underanswer / stop_when_sufficient` 下的行为差异 | 很早就确认了 post-training 会系统性改变 boundary behavior，base 更 raw，chat 更 assistant-like | 变量太多同时变化：checkpoint、template、接口、官方 post-training；而且 mode 仍集中在主线边界轴，不是多轴 controllability | 需要同类强模型上、跨多个轴、统一接口的 prompt-only controllability matrix |
| Qwen base vs instruct 粗对照 | `results/qwen_base_vs_instruct_proxy_v1.jsonl` | `qwen2.5-7b-base` vs `qwen2.5-7b-instruct` | `neutral / avoid_underanswer / no_extra_help / scope_minimal` | 再次支持 post-training strongly reshapes controllability；并且显示“不要额外帮助”和“短答/收边界”不是同一回事 | 仍是主线边界相关的少数 mode；没有去测其它高层轴是否也难压；也不是统一 benchmark | 需要把 interaction / next-step / caveat 等轴纳入同一套现成模型 eval |
| Mistral base vs instruct 粗对照 | `results/mistral_base_vs_instruct_proxy_v1.jsonl` | `Mistral-7B-v0.3` vs `Mistral-7B-Instruct-v0.3` | 同上 | 说明这种粗粒度差异不只出现在一个家族上 | 和 Qwen 粗对照同样的问题：只支持“post-training matters”，不支持“哪些轴会损伤 controllability” | 同上，需要多轴 paired controllability eval |
| Qwen 主现象确认 | `results/qwen_final_confirmation_fixed_v2.jsonl` | `qwen2.5-7b-instruct` | 主线边界轴的再次确认 | 现成强 instruct 模型上，short-answer / scope-breadth 类失败模式能看见 | 只测了主线轴，没有测别的轴；因此不能用它证明“只有这条轴特殊” | 需要同一模型上补其它高层轴的正反向 controllability |
| Mistral 主现象确认 | `results/mistral_final_confirmation_fixed_v1.jsonl` | `Mistral-7B-Instruct-v0.3` | 主线边界轴的再次确认 | 现成 instruct 模型上，主线现象不是 Qwen 特例 | 同样只覆盖主线轴 | 需要同模型上测其它高层轴 |
| Assistant family compare（Qwen / Mistral） | `results/assistant_family_compare_v1.jsonl`, `results/assistant_family_mistral_v1.jsonl` | `qwen25_instruct`, `mistral_instruct_v03` | 少量主线 mode 的跨模型对比 | 支持“主现象方向在不同现成 instruct 模型上大体一致” | 还是围绕主线边界轴；不是 multi-axis controllability | 需要扩成真正的多轴 benchmark |
| Qwen / Mistral additional evidence & final confirmation 系列 | `results/qwen_main_evidence_16_v1/v2.jsonl`, `results/mistral_cross_model_support_8_v1.jsonl` 等 | 现成 instruct 模型 | 主线边界轴的更大样本确认 | 强化了 short-answer / boundary 轴的重要性 | 仍未覆盖其它轴；没有明确判断“别的轴是否同样难控” | 缺 cross-axis benchmark，而不是更多主线确认 |
| SmolLM2 英文 second-family replication | `mechanism_experiment/outputs/smollm2_*`, 文档中多个总结文件 | `HuggingFaceTB/SmolLM2-1.7B-Instruct` | 训练 family 的英文 second-family directional replication | 支持主线不是中文 Qwen 特例，至少有 cross-family、cross-language directional replication | 它测的是主线 family 的方向性复制，不是现成模型上其它轴的 prompt-only controllability | 缺现成强英文模型上的多轴 prompt-only controllability 对照 |
| `emoji_only` SFT / 浅表对照 | `scripts/run_train_emoji_only_v1_1p5b_logged.ps1`, `mechanism_experiment/outputs/qwen25_1p5b_emoji_only_*` | 自训浅表 style 方向 | 浅表格式/表情风格是否 sticky | 说明浅表轴和主线高层轴不同；不是所有方向都同样 sticky | 这不是外界模型 eval；而且它更像 shallow-style 对照，不回答现成强模型的其它高层轴 controllability | 如果要用作现成模型对照，需要在现成模型上直接做 emoji / bullet benchmark |

---

## 这些旧线最接近现在问题的，是哪几类

如果只看“和现在这个问题最接近”的旧线，其实主要是三类：

1. **taxonomy / mixed discovery**
   - 因为它们确实碰过：
     - warm
     - proactive
     - no extra comfort
     - more detailed
     - do not add unasked help
   - 但它们主要证明的是“会不会被 prompt 拨动”，不是“反向能不能压回去”。

2. **base vs chat / base vs instruct 粗对照**
   - 因为它们明确比较了：
     - post-training 前后
     - boundary behavior 的差异
   - 但它们主要回答的是：
     - post-training 改变很大
   - 不是：
     - 哪些其它轴也会伤用户 controllability。

3. **Qwen / Mistral / SmolLM2 的主线确认**
   - 它们说明主线现象在外部模型上不是孤立 artifact。
   - 但它们几乎都还是围绕：
     - `short-answer / scope / no-extra-help`
   - 所以不能推出：
     - 其它高层轴也一样
     - 或只有这条轴特殊

---

## 为什么这些旧线还不够

核心缺口不是“没有外界模型”，而是**没有多轴、同构、正反向 controllability benchmark**。

更具体地说，旧线主要缺 4 件事：

### 1. 缺 paired axis
很多旧线只有：
- `more detailed`
- `more proactive`
- `more warm`

但没有配成同等地位的：
- `less detailed`
- `no extra help`
- `no extra warmth`

更没有围绕“用户要求反向时能不能压回去”来设计。

### 2. 缺统一评分目标
旧线很多时候看的是：
- 平均长度
- 定性响应风格
- 若干例子

但没有统一问：
- 是否 obey 目标 mode
- 是否仍然出现被禁止行为
- 哪一侧更难被 prompt 压回

### 3. 缺真正和主线并列的其它高层轴
旧线真正系统确认过的是：
- short-answer / scope
- no extra help（部分）

但没有把下面这些做成同等级 benchmark：
- `add_one_next_step` vs `no_next_step`
- `more_complete_caveat` vs `no_extra_caveat`
- `clarify_first` vs `answer_first`

### 4. 缺在“现成强模型”上的统一比较
现在最需要的不是再找更多零散文件，而是统一在：
- GPT 系列
- DeepSeek chat/instruct
- 其它现成强模型

上做同一套多轴 eval。

---

## 因而现在真正缺什么

如果目标是回答：

> 到底是 short-answer / scope 轴特殊，还是后训练更一般地损伤了用户对某些轴的 controllability？

那现在缺的是下面这件事，而不是更多旧线梳理：

### 缺一个现成强模型 multi-axis controllability benchmark

建议至少包括：

#### 主轴
1. `short-answer / scope-minimal`
2. `add_one_next_step / no_next_step`
3. `more_complete_caveat / no_extra_caveat`

#### 次轴
4. `clarify_first / answer_first`

#### 浅表对照
5. `emoji` 或 `bullet points`

并在每个模型上统一看：
- 正向 mode 是否生效；
- 反向 mode 是否也能同样有效；
- 哪些轴更容易出现单向 sticky / harder-to-suppress behavior。

---

## 最后一句话

以前的外界模型 eval 不是没做，而是**做得很多，但大多是主线边界轴确认、prompt-bendability 探索、或 base-vs-chat 粗对照**。  
它们足以支持：

- post-training strongly reshapes controllability；
- 主线现象不是单一中文 Qwen artifact；
- 很多高层方向会被 prompt 拨动，而且常常 bundle 在一起。

但它们**还不足以直接回答**：

- 是不是只有 short-answer / scope 轴特别难压；
- 还是后训练更一般地损伤了用户对多个高层轴的 controllability。

这就是现在还缺的那一块。
