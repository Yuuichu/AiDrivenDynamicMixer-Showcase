# Screenshots

One screenshot is included; the rest of this list still requires a human with the right host running.

## Captured

| File | Shows |
|---|---|
| `report.png` | The full HTML report for the bundled synthetic session, rendered headlessly: session/track table, feature summary, spatial summary, all 8 detected `dialogue_masking` issues with severities and time ranges, and all 8 recommendations with `Human review: yes` |

This is genuine tool output from the repository's own example stems, so it exposes no production material.

## What should be captured next

1. **`cli-run.png`** — the CLI invocation that produces the artefacts, showing the output paths.
2. **`cli-run.png`** — the CLI run that produces the artefacts, showing the output paths.
2. **`spatial-fixture.png`** — a **stereo** synthetic fixture demonstrating `spatial_conflict` and `dialogue_wider_than_expected`. The current demo is mono, so these criteria are not visible yet; this capture requires building a stereo fixture first.
5. **`reaper-window.png`** — the analysed stems in REAPER with a finding's time range selected, closing the loop from report to session.

## Constraints on what may be shown

- **Synthetic or self-owned material only.** No client sessions, no production VO, no project or track names from real work — on-screen or in filenames.
- **No absolute local paths**, and in particular no directory names that identify a client or product.
- No API keys or tokens (the tool does not need any, which is itself worth showing).
- The tool never modifies a session; any capture should not imply otherwise.

## Why screenshots are constrained here

This is the one project in the set where the risk of incidental disclosure is highest: a mix-diagnosis tool is normally pointed at real material, and its natural screenshots — track lists, file names, VO character names, report titles — are exactly the things that identify a client project. Every capture must come from synthetic fixtures.