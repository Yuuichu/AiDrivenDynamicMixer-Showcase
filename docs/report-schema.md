# Report schema

> **English** | [简体中文](report-schema.zh-CN.md)

Four JSON documents plus an HTML rendering. The same structures are what a future model adapter would consume, which is why they are specified explicitly rather than being incidental output.

All timestamps are **seconds** (floats); all levels are **dBFS approximations**.

## `session.json` — what was analysed

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

| Field | Meaning |
|---|---|
| `host` | Source host: `reaper` (stems) or `wwise` (telemetry) |
| `frame_ms` | Analysis frame length — the time resolution of every finding |
| `tracks[].role` | Semantic role (`dialogue`, `music`, `ambience`, …). Rules are written against roles, not filenames |
| `tracks[].source` | Where the track came from — a file path for stems, a reference for telemetry |
| `host_ref` | Host-side identifier, so a finding can be located in the original session |
| `sample_rates_mixed` | Flags a set of stems recorded at inconsistent rates |

## `features.json` — the measured timeline

The full per-frame feature timeline: 8-band energy, loudness, L-R correlation and stereo width per track. This is the evidence layer: every issue's `evidence` block is a direct readout from here, which is what makes findings auditable.

Write this to a different location than the reports if size matters; it is the largest artefact by an order of magnitude.

## `issues.json` — what was found

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

| Field | Meaning |
|---|---|
| `issue_type` | `dialogue_masking`, `spatial_conflict`, `dialogue_wider_than_expected` |
| `time_start` / `time_end` | Frame-accurate range — the actionable part |
| `target` | What is being harmed (usually dialogue) |
| `masker` | What is causing it |
| `severity` | 0.1–1.0, from the documented formula (not a probability) |
| `evidence` | The measured numbers the decision was made from |
| `reason` | Human-readable statement, generated from the same numbers |

## `recommendations.json` — what could be done

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

Two fields carry the project's position:

- **`requires_human_review: true`** — always true. A recommendation is a proposal.
- **`host_mapping_hint`** — deliberately expressed as an instruction to a human ("map this … after human approval"), not as an automation payload, because the tool does not write to the host.

## `spatial_summary.json` — the spatial picture

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

The `spatial_available` / `spatial_degraded` flags matter: a **mono** track has no stereo image to conflict with, and is marked unavailable rather than being scored as perfect coherence. Without that distinction, every mono ambience would look like an ideal centre image.

## `report.html` — the human view

A self-contained HTML document (inline CSS, no external asset dependencies) containing the session summary, per-track feature rollups and the issue list. It is the artefact a mixer actually opens; the JSON is what a pipeline consumes.

## Per-second and spatial report modules

The report package also contains modules that aggregate findings into a per-second action list and a spatial breakdown. Those modules currently carry **project-specific track-name mappings and a report title** in the private source, and are therefore not included in this showcase — see `PUBLICATION_CHECKLIST.md`. They must be made generic before any of this is published.