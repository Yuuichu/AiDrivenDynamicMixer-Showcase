# Licence and third-party notice

## AiDrivenDynamicMixer

The project's repository does **not** currently contain a `LICENSE` file, so this showcase makes no licence claim and does not reproduce one. Absence of a licence here is not permission to reuse the code.

If a licence is intended, adding the canonical `LICENSE` to the main repository is the first step; this notice should then be updated to match.

## Third-party software

| Component | Role | Licence |
|---|---|---|
| `numpy` | Optional accelerator for band analysis (the tool runs without it) | BSD-3-Clause |
| `REAPER` | Host, via Lua adapters | Commercial — Cockos Incorporated |
| `Wwise` | Host, via project reader / telemetry importer | Commercial — Audiokinetic Inc. |

Neither REAPER nor Wwise is included, linked against, or redistributed. The adapters are independent scripts/readers that operate inside a licensed installation.

## Audio and session content

**No audio and no session material is included.**

The demo artefacts under `demo/` were produced from the repository's **synthetic example stems** (generated test material: one dialogue line, one music pad, one low ambience). No production or client session was analysed to produce them.

## Publication blocker (read before publishing)

The private source contains **project-specific strings** that must not be published:

- `core/reports/per_second.py` contains hardcoded report titles and a **track-name mapping table keyed by real project track IDs**.
- The private `out/` directory contains a **complete analysis run against a real project**, including a client project directory name and VO character names.

`out/` is covered by `.gitignore` and is not part of the committed tree, but the hardcoded strings in `per_second.py` **are** in source. They must be removed (or the modules excluded) before this project is pushed anywhere — see `PUBLICATION_CHECKLIST.md`.

This showcase excludes both: the per-second report modules are not included, and the demo was regenerated from synthetic stems. The one generated file that inherited a hardcoded title (`per_second_actions.md`) was removed from this showcase.