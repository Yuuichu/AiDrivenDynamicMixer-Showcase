# Demo

Everything in this directory was produced by the tool itself, from the repository's **synthetic example stems** — a dialogue line, a music pad and a low ambience generated for testing. No production session was analysed to create these files.

## Files

| File | Content |
|---|---|
| `session.json` | The analysed session: three tracks with roles, 250 ms frames, 3.0 s duration |
| `issues.json` | 8 detected issues, all `dialogue_masking` (`music_pad` masking `dialogue_main` in the clarity bands) |
| `recommendations.json` | The corresponding recommendations, each with `requires_human_review: true` and REAPER/Wwise mapping hints |
| `spatial_summary.json` | Per-track spatial rollups. The example stems are mono, so tracks are marked `spatial_available: false` rather than scored as perfect coherence |
| `report.html` | The self-contained HTML report — the artefact to open first |

## Why the example is small

Three seconds and three tracks is enough to demonstrate the full contract — features, detection, evidence, recommendations, HTML report — without shipping audio. A larger demo would be more impressive and less honest, because its numbers would depend on material that cannot be published.

## What the example does and does not show

- **Shows:** the pipeline end to end, the JSON contract, the severity/evidence structure, the human-review flags, and the mono-vs-stereo distinction.
- **Does not show:** spatial-conflict detection on real stereo material. The example stems are mono, so only `dialogue_masking` issues appear here. The spatial criteria are implemented and documented in `docs/method.md`, but a synthetic stereo fixture is needed to demonstrate them — that is a worthwhile addition.

## Reproducing this demo

```bash
python -m apps.cli analyze-reaper \
  --stems examples/reaper_cutscene/stems \
  --out <output-directory>
```

The per-second action report and the spatial HTML report are additional outputs of the same run, but they are **not** included here: their modules carry project-specific track-name mappings and a report title in the private source, and must be made generic first. See `PUBLICATION_CHECKLIST.md`.