> [English](report-schema.md) | **简体中文**

# 报告 schema

四份 JSON 文档加一份 HTML 渲染。这些结构也正是未来某个模型适配器将要消费的东西，这就是它们被明确定义、而不是当作附带产物的原因。

所有时间戳都是**秒**（浮点数）；所有电平都是 **dBFS 近似值**。

## `session.json` —— 分析了什么

```json
{
  "id": "stems",
  "host": "reaper",
  "sample_rate": 16000,
  "duration_seconds": 3.0,
  "frame_ms": 250,
  "tracks": [
    { "id": "dialogue_main", "name": "dialogue_main", "role": "dialogue",
      "source": "stems\\dialogue_main.wav", "host_ref": "stem:2" }
  ],
  "metadata": { "input": "stems", "sample_rates_mixed": false }
}
```

| 字段 | 含义 |
|---|---|
| `host` | 来源宿主：`reaper`（分轨）或 `wwise`（遥测） |
| `frame_ms` | 分析帧长——每项发现的时间分辨率 |
| `tracks[].role` | 语义角色（`dialogue`、`music`、`ambience`、……）。规则是针对角色写的，不是针对文件名 |
| `tracks[].source` | 轨道来自哪里——分轨是文件路径，遥测是引用 |
| `host_ref` | 宿主侧标识符，因此可以在原始工程中定位某条发现 |
| `sample_rates_mixed` | 标记一组以不一致采样率录制的分轨 |

## `features.json` —— 测量出的时间线

完整的逐帧特征时间线：逐轨的 8 频段能量、响度、L-R 相关性与立体声宽度。这是证据层：每个问题的 `evidence` 块都是从这里直接读出的，这正是发现可被审计的原因。

如果在意体积，请把它写到与报告不同的位置；它是最大的产物，比其余大一个数量级。

## `issues.json` —— 发现了什么

```json
[
  {
    "id": "issue_1",
    "issue_type": "dialogue_masking",
    "time_start": 0.5,
    "time_end": 0.75,
    "target": "dialogue_main",
    "masker": "music_pad",
    "severity": 0.41,
    "reason": "music_pad overlaps dialogue clarity bands near dialogue_main.",
    "evidence": { "target_clarity_db": -85.06, "masker_clarity_db": -83.63 }
  }
]
```

| 字段 | 含义 |
|---|---|
| `issue_type` | `dialogue_masking`、`spatial_conflict`、`dialogue_wider_than_expected` |
| `time_start` / `time_end` | 帧级精确的范围——可据以行动的部分 |
| `target` | 受到损害的对象（通常是对白） |
| `masker` | 造成损害的东西 |
| `severity` | 0.1–1.0，来自已记录的公式（不是概率） |
| `evidence` | 做出该判断所依据的测量数字 |
| `reason` | 人类可读的陈述，由同样的数字生成 |

## `recommendations.json` —— 可以做什么

```json
[
  {
    "id": "rec_1",
    "issue_id": "issue_1",
    "time_start": 0.5,
    "time_end": 0.75,
    "target": "music_pad",
    "operation": "dynamic_eq_ducking",
    "suggested_amount": {
      "band_hz": [1250, 5000],
      "gain_db": -2.5,
      "attack_ms": 120,
      "release_ms": 700
    },
    "confidence": 0.35,
    "reason": "music_pad overlaps dialogue clarity bands near dialogue_main.",
    "requires_human_review": true,
    "host_mapping_hint": {
      "reaper": "Map to an EQ band gain envelope on the masker track after human approval.",
      "wwise": "Map to Meter/RTPC-driven ducking or snapshot EQ on the masker bus after human approval."
    }
  }
]
```

有两个字段承载着项目的立场：

- **`requires_human_review: true`** —— 永远为 true。一条建议就是一个提议。
- **`host_mapping_hint`** —— 刻意表述为对人的指示（「在人工批准之后再映射它……」），而不是自动化载荷，因为这个工具不向宿主写入。

## `spatial_summary.json` —— 空间图景

```json
{
  "tracks": [
    { "track_id": "ambience_low", "role": "ambience",
      "channel_count": 1, "spatial_available": false, "spatial_degraded": false,
      "avg_pan": 0.0, "avg_width": 0.0, "avg_correlation": 1.0,
      "avg_distance_proxy": 0.0, "avg_brightness_db": -120.0 }
  ],
  "issues": [ /* spatial-conflict issues */ ]
}
```

`spatial_available` / `spatial_degraded` 这两个标记很重要：**单声道**轨道没有可冲突的立体声声像，它被标记为不可用，而不是被评为完美相干。没有这个区分，每一段单声道环境声都会看起来像理想的中央声像。

## `report.html` —— 给人看的视图

一份自包含的 HTML 文档（内联 CSS，无外部资源依赖），包含会话摘要、逐轨特征汇总与问题列表。它才是混音师真正会打开的东西；JSON 则是管线消费的东西。

## 逐秒与空间报告模块

报告包中还包含把发现聚合为逐秒行动清单与空间分解的模块。这些模块目前在私有源码里带有**项目特定的轨道名映射与一个报告标题**，因此未收录进本展示仓库——见 `PUBLICATION_CHECKLIST.md`。在发布任何相关内容之前，必须先让它们泛化。