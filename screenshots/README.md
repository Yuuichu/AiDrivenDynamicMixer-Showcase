# Screenshots

Empty in this draft. The HTML report in `demo/report.html` already shows the output format; what is missing is the tool in use, and capturing that against a real session would risk exposing client material.

## What should be captured

1. **`hero-report.png`** — `demo/report.html` rendered in a browser. The report is the product's face, and it can be captured from the synthetic demo without any risk.
2. **`cli-run.png`** — the CLI run that produces the artefacts, showing the output paths.
3. **`issues-table.png`** — the issue list with severity and time ranges, which is the "evidence, not vibes" story in one image.
4. **`spatial-fixture.png`** — a **stereo** synthetic fixture demonstrating `spatial_conflict` and `dialogue_wider_than_expected`. The current demo is mono, so these criteria are not visible yet; this capture requires building a stereo fixture first.
5. **`reaper-window.png`** — the analysed stems in REAPER with a finding's time range selected, closing the loop from report to session.

## Constraints on what may be shown

- **Synthetic or self-owned material only.** No client sessions, no production VO, no project or track names from real work — on-screen or in filenames.
- **No absolute local paths**, and in particular no directory names that identify a client or product.
- No API keys or tokens (the tool does not need any, which is itself worth showing).
- The tool never modifies a session; any capture should not imply otherwise.

## Why screenshots are constrained here

This is the one project in the set where the risk of incidental disclosure is highest: a mix-diagnosis tool is normally pointed at real material, and its natural screenshots — track lists, file names, VO character names, report titles — are exactly the things that identify a client project. Every capture must come from synthetic fixtures.