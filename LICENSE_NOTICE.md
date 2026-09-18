# Licence and third-party notice

## AiDrivenDynamicMixer

Released under the **MIT licence** (`Copyright (c) 2026 Yuuichu`). The full licence text is included in this showcase as `LICENSE`, and the same file lives in the development repository.

## Third-party software

| Component | Role | Licence |
|---|---|---|
| `numpy` | Optional accelerator for band analysis (the tool runs without it) | BSD-3-Clause |
| `REAPER` | Host, via Lua adapters | Commercial — Cockos Incorporated |
| `Wwise` | Host, via project reader / telemetry importer | Commercial — Audiokinetic Inc. |

Neither REAPER nor Wwise is included, linked against, or redistributed. The adapters are independent scripts/readers that operate inside a licensed installation.

## Audio and session content

**No audio and no session material is included.**

No generated analysis output is included in this showcase. The example telemetry input under `examples/` is the repository's **synthetic test material** (generated: one dialogue line, one music pad, one low ambience). No production or client session was analysed to produce any of it.

## Sanitization record

The private source previously contained **project-specific strings**:

- `core/reports/per_second.py` hardcoded a report title and a **track-name mapping table keyed by real project track IDs**; `_action_for` was likewise keyed on those IDs.
- The private `out/` directory contained a **complete analysis run against a real production project** (project directory name, VO character names, asset paths).

**Resolved before publication:**

1. `per_second.py` was rewritten to derive track labels **generically** — a leading numeric index prefix is stripped and a `_vo_` convention is honoured — so no table of known ids ships. Duplication rules now match on label keywords instead of hardcoded ids. Verified by re-running the pipeline (`tests`: 5 passed) and by scanning the module, the working tree and **every reachable git object** for the previous identifiers: zero matches.
2. `out/` was moved out of the project to a quarantine directory outside the repository, so no production analysis is present in the working tree.
3. All generated demo output was then dropped from this showcase entirely; the one file that had inherited a hardcoded title was removed first.

The remaining `out/` exclusion is therefore a build-artefact exclusion only, not a content restriction.