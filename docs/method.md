# Method

The analysis answers a narrow question: **where, and by how much, does something interfere with intelligibility or the spatial image?** It answers with numbers and time ranges, and it never changes the session.

## 1. Feature extraction — parameterised, not raw audio

Each track is analysed frame by frame (default frame length 250 ms) to produce:

| Feature | Notes |
|---|---|
| **8-band energy** | `40-80`, `80-160`, `160-320`, `320-640`, `640-1250`, `1.25k-2.5k`, `2.5k-5k`, `5k-10k` Hz |
| **Loudness** | dBFS approximation |
| **L/R correlation** | Stereo coherence, `+1` = mono-compatible |
| **Stereo width** | Side/mid relationship |
| **Spatial availability** | Whether the source even has spatial information (mono tracks are marked unavailable rather than scored as perfect) |

Implementation notes:

- WAV reading uses the **standard library**; no heavy audio dependency is required to run the analysis.
- Sliding-window band analysis uses the **Goertzel algorithm** rather than a full FFT, since only eight bands need measuring.
- **numpy is optional** — an accelerator, not a prerequisite.

What this layer deliberately is *not*: a raw-sample or full-STFT pipeline. Features are few, named and reproducible, which is what allows the report to be argued with and what keeps the analysis cheap.

## 2. Detection criteria

### Dialogue masking

Evaluated per frame, in the **speech-clarity bands** only: `1.25k-2.5k` and `2.5k-5k`. Consonant intelligibility lives there; masking elsewhere is a different (and less urgent) problem.

```text
if dialogue_loudness_db > -60                              # dialogue is actually present
   and (masker_clarity_db - dialogue_clarity_db) >= -3.0:  # masker is close to or above dialogue
        issue = dialogue_masking
        severity = min(1.0, max(0.1, (masker_clarity_db - dialogue_clarity_db + 6.0) / 18.0))
```

Reading the severity formula: a 3 dB gap yields the 0.1 floor, a bigger overlap rises toward 1.0, and the `+6 / 18` scaling was chosen so the useful range is fully spanned rather than saturating immediately.

The `> -60 dBFS` guard matters: without it, silence would be reported as masking, since two very quiet tracks can be "within 3 dB" of each other indefinitely.

### Spatial conflict

```text
if track_loudness_db > -55.0
   and lr_correlation < -0.2
   and stereo_width  > 0.4:
        issue = spatial_conflict
```

All three conditions are required. Loudness gates it (a silent track cannot conflict with anything), correlation catches anti-correlated material, and width catches material that is too wide to sit in an image.

### Dialogue wider than a centre image

A third check, distinct from the textbook one:

```text
if dialogue is spatially active
   and stereo_width > 0.4:
        issue = dialogue_wider_than_expected
```

A dialogue stem does not need negative correlation to be a problem: excessive width alone degrades intelligibility and localisation, so it is reported separately rather than folded into the correlation test.

## 3. Recommendations

Detected issues are converted into concrete operations by a **deterministic rule engine** (`core/ai_reasoning/rule_engine.py`) — no model call, no randomness, same input → same output.

Each recommendation contains:

- the **operation** (e.g. `dynamic_eq_ducking`),
- **suggested amounts**: band range, gain in dB, attack and release times,
- a **confidence** value,
- `requires_human_review: true`,
- a **host mapping hint** for REAPER and for Wwise, each phrased as an instruction to a human reviewer.

Example (illustrative, from the repository's synthetic example stems): `music_pad` overlapping `dialogue_main` in the clarity bands produces a ducking recommendation for 1250–5000 Hz, −2.5 dB, 120 ms attack, 700 ms release, confidence ≈ 0.35.

Low confidence plus a mandatory review flag is the intended behaviour: the tool's job is to point at a specific moment, not to decide.

## 4. What the tool will not do

- It does not write automation, RTPCs, snapshots or project files.
- It does not render or modify audio.
- It does not decide that a mix is finished.

The REAPER and Wwise adapters exist to *read* stems, project data and telemetry. Their read-only nature is the design, not a limitation to be lifted later.

## 5. Known weaknesses

- **Loudness is an approximation**, not BS.1770, so absolute thresholds should be read as heuristics.
- **Band energy is not perceptually weighted**, so a "3 dB" gap is a level statement, not a loudness statement.
- **Masking is not modelled psychoacoustically.** There is no simultaneous-masking curve here; the criteria are level-and-band heuristics that are documented so they can be tuned.
- **Frame resolution limits time precision** — findings land on frame boundaries (250 ms by default).
- **Thresholds were tuned on example material** and should be revisited per genre or per project.