> [English](README.md) | **简体中文**

# AiDrivenDynamicMixer

跨宿主的混音诊断：分析离线分轨或运行时遥测，定位**对白掩蔽**与**空间冲突**，产出可复核的 JSON/HTML 报告——且绝不修改工程。

## 为什么做这个

为可懂度做混音，是这份工作里最难靠耳朵快速完成的部分。对白可能被音乐床或环境声埋掉，枪声可能糊掉一句台词的清晰度频段，立体声 pad 可能把中央声像压塌——而当你整段听一遍而不是只盯那关键的 40 秒时，这些都很容易被漏掉。

现有能帮上忙的工具，要么是计量表（显示的是电平，不是冲突），要么是全自动混音（替混音师做艺术决策）。我想要的是中间地带：**证据，带精确时间范围，以人可以核查并据以行动的形式呈现**。

由此产生两条约束，它们定义了这个项目：

1. **工具不得触碰工程。** 不写自动化、不写 RTPC、不写快照、不改动工程。它只产出建议，由人来做决定。
2. **分析必须可解释。** 每一项发现都必须能追溯到某个数值判据，因此混音师可以核验这个判断，而不是去信任一个模型。

## 功能概览

- **两条输入路径，一个分析核心：** 离线 REAPER 分轨（WAV）或 Wwise 风格的运行时遥测（JSON）。
- **参数化的特征提取：** 逐轨、逐帧的 8 频段能量时间线，外加响度、L/R 相关性与立体声宽度。
- **对白掩蔽检测**，在语音清晰度频段上进行，带严重度评分与帧级精确的时间范围。
- **空间冲突检测**，基于相关性、宽度与电平——包括对白宽到不适合中央声像的情况。
- **带复核标记的建议：** 每个问题都对应一个具体操作（例如带增益/启动/释放的限频段闪避），并标记 `requires_human_review`，另附逐宿主的映射提示。
- **可复核的输出：** `session.json`、`features.json`、`issues.json`、`recommendations.json`，外加一份 HTML 报告、一份逐秒行动清单和一份空间摘要。

## 工作流

```text
Stems (WAV)  /  Wwise telemetry (JSON)
        |
        v
Feature extraction       8 bands + loudness + L/R correlation + stereo width, per frame
        |
        v
Detection                dialogue masking  |  spatial conflict
        |
        v
Explainable report       issues with severity, evidence, and exact time ranges
        |
        v
Recommendations          concrete operations, requires_human_review = true
        |
        v
Human review -> applied by hand in REAPER / Wwise
```

## 技术要点

- **参数化的特征层，刻意不做原始音频。** 不会把采样数据或完整 STFT 矩阵发到任何地方。特征只计算一次、可复现，报告正是基于它们写成的。这让分析可审计且成本低——也正是日后引入模型时无需改变契约的原因。
- **八个固定频段**，覆盖 40 Hz 到 10 kHz（`40-80`、`80-160`、`160-320`、`320-640`、`640-1250`、`1.25k-2.5k`、`2.5k-5k`、`5k-10k`）。
- **语音清晰度频段是明确选定的。** 掩蔽只在 `1.25k-2.5k` 与 `2.5k-5k` 评估，也就是承载辅音可懂度的区域——而不是整个频谱。
- **可以直接从源码读出的阈值。** 对白掩蔽：掩蔽源在清晰度频段的均值与对白的差值在 3 dB 以内，同时对白响度高于 −60 dBFS。严重度：`clamp((Δ + 6) / 18, 0.1, 1.0)`。空间冲突：L/R 相关性低于 −0.2、立体声宽度高于 0.4、响度高于 −55 dBFS。
- **教科书之外还有第三项空间检查。** 宽于中央声像应有宽度的对白会被单独标记——对白分轨上的相位/加宽问题即使单看相关性还算可接受，也会损害可懂度。
- **帧级精确，而不是轨级。** 每项发现都带 `time_start` / `time_end`，因为「音乐太响了」无法据以行动，而「音乐在 00:00:00.500–00:00:00.750 掩蔽了对白」可以。
- **人在回路被强制写进数据模型。** 每条建议都带 `requires_human_review: true`，每一条宿主映射提示都表述为「在**人工批准之后**再映射它……」。
- **默认只用标准库。** WAV 读取使用标准库；窄带分析使用 Goertzel 算法，numpy 是可选的加速器而非必需项。

## 架构

```text
core/
  audio_features/   band energy, loudness, correlation, width  (Goertzel / optional numpy)
  masking/          dialogue-masking and spatial-conflict criteria
  spatial_features/ spatial analysis
  ai_reasoning/     deterministic rule engine -> recommendations
  reports/          HTML, per-second and spatial report modules
  schemas/          the data contract (session, issue, recommendation)
adapters/
  reaper/           stem export helpers (Lua) — never modifies the session
  wwise/            project reader and telemetry importer
apps/               CLI entry points
```

`docs/method.zh-CN.md` 记录检测判据；`docs/report-schema.zh-CN.md` 记录 JSON 契约。

## 我的角色

独立作者：分析设计、特征提取、检测判据、规则引擎、报告生成、REAPER/Wwise 适配器以及 CLI。

## 局限与边界

以下是刻意的边界，而不是路线图：

- **v1 是确定性的规则引擎。** 推理路径中没有 LLM。schema 为将来的模型预留了一个适配器位置，但本仓库中没有任何东西调用模型，报告由固定规则生成——天生可复现。
- **这个工具不修改任何东西。** 它产出报告和建议。写自动化、RTPC 或快照被明确排除在范围之外，适配器也按只读构建。
- **建议是起点，不是答案。** 置信度按设计就偏低（随附示例得分 ≈ 0.35），且 `requires_human_review` 永远为 true。混音是审美决策。
- **响度是近似值**，不是 ITU-R BS.1770 测量，且频段能量是逐帧的，没有做感知加权。
- **阈值是启发式的**，在示例素材上调过；它们之所以写在源码里，正是为了让人可以质疑。
- **轨道标签是启发式推导的。** 逐秒报告从轨道 id 推导短标签（剥掉数字索引前缀，遵循 `_vo_` 约定），并按标签关键词匹配修复规则，因此不常见的命名约定可能给出比手工定制的映射更不具体的建议。
- **仅使用合成夹具。** 随附的示例是生成的测试素材；这个工具没有在大量真实工程上验证过。

## 仓库范围

这是一个作品集展示仓库。完整开发仓库保持私有。

包含：`selected-code/` 中的掩蔽/规则引擎/报告核心、CLI 可见的数据契约，以及 `examples/telemetry-example.json` 中的示例遥测输入。不包含：来自真实工程的会话分析输出、REAPER/Wwise 适配器实现，以及生产音频。

## 技术栈

`Python 3.11+` · standard-library WAV I/O · `Goertzel` narrow-band analysis · band-energy / loudness / L-R correlation / stereo width · deterministic rule engine + JSON Schema · `REAPER Lua` adapter · `Wwise` telemetry adapter · HTML report generation · `pytest`