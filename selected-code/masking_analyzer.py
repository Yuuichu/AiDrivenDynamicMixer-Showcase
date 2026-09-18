from __future__ import annotations

from core.schemas import Issue, TrackFeatureTimeline

CLARITY_BANDS = ("1.25k-2.5k", "2.5k-5k")
LOW_BANDS = ("40-80", "80-160", "160-320")


def _avg(values: list[float]) -> float:
    return sum(values) / len(values) if values else -120.0


def _band_avg(frame, bands: tuple[str, ...]) -> float:
    return _avg([frame.band_db.get(band, -120.0) for band in bands])


def _issue_span(frame_index: int, frame_ms: int) -> tuple[float, float]:
    start = frame_index * frame_ms / 1000.0
    return start, start + frame_ms / 1000.0


def analyze_issues(timelines: list[TrackFeatureTimeline]) -> list[Issue]:
    issues: list[Issue] = []
    by_id = {timeline.track_id: timeline for timeline in timelines}
    dialogue_tracks = [timeline for timeline in timelines if timeline.role in {"dialogue", "primary_dialogue", "voice"}]
    maskers = [timeline for timeline in timelines if timeline.role not in {"dialogue", "primary_dialogue", "voice"}]

    issue_counter = 1
    for target in dialogue_tracks:
        for masker in maskers:
            frame_count = min(len(target.frames), len(masker.frames))
            for idx in range(frame_count):
                target_frame = target.frames[idx]
                masker_frame = masker.frames[idx]
                target_clarity = _band_avg(target_frame, CLARITY_BANDS)
                masker_clarity = _band_avg(masker_frame, CLARITY_BANDS)
                if target_frame.loudness_db > -60 and masker_clarity - target_clarity >= -3.0:
                    start, end = _issue_span(idx, target.frame_ms)
                    severity = min(1.0, max(0.1, (masker_clarity - target_clarity + 6.0) / 18.0))
                    issues.append(
                        Issue(
                            id=f"issue_{issue_counter}",
                            issue_type="dialogue_masking",
                            time_start=start,
                            time_end=end,
                            target=target.track_id,
                            masker=masker.track_id,
                            severity=severity,
                            reason=f"{masker.track_id} overlaps dialogue clarity bands near {target.track_id}.",
                            evidence={
                                "target_clarity_db": round(target_clarity, 2),
                                "masker_clarity_db": round(masker_clarity, 2),
                            },
                        )
                    )
                    issue_counter += 1

    for timeline in timelines:
        for idx, frame in enumerate(timeline.frames):
            active_for_spatial = frame.loudness_db > -55.0
            if (
                timeline.spatial_available
                and frame.lr_correlation is not None
                and frame.lr_correlation < -0.2
                and frame.stereo_width is not None
                and frame.stereo_width > 0.4
            ):
                start, end = _issue_span(idx, timeline.frame_ms)
                issues.append(
                    Issue(
                        id=f"issue_{issue_counter}",
                        issue_type="phase_risk",
                        time_start=start,
                        time_end=end,
                        target=timeline.track_id,
                        masker=None,
                        severity=min(1.0, abs(frame.lr_correlation)),
                        reason=f"{timeline.track_id} has low or negative L/R correlation.",
                        evidence={"lr_correlation": frame.lr_correlation, "stereo_width": frame.stereo_width},
                    )
                )
                issue_counter += 1

            if (
                active_for_spatial
                and timeline.spatial_available
                and timeline.role in {"dialogue", "primary_dialogue", "voice"}
                and frame.stereo_width is not None
                and frame.stereo_width > 0.5
            ):
                start, end = _issue_span(idx, timeline.frame_ms)
                issues.append(
                    Issue(
                        id=f"issue_{issue_counter}",
                        issue_type="overwide_dialogue",
                        time_start=start,
                        time_end=end,
                        target=timeline.track_id,
                        masker=None,
                        severity=min(1.0, frame.stereo_width),
                        reason=f"{timeline.track_id} dialogue is wider than expected for center clarity.",
                        evidence={"stereo_width": frame.stereo_width, "pan_estimate": frame.pan_estimate},
                    )
                )
                issue_counter += 1

            if active_for_spatial and timeline.spatial_available and timeline.role in {"music"} and frame.stereo_width is not None and frame.stereo_width < 0.08 and frame.loudness_db > -45:
                start, end = _issue_span(idx, timeline.frame_ms)
                issues.append(
                    Issue(
                        id=f"issue_{issue_counter}",
                        issue_type="narrow_music_field",
                        time_start=start,
                        time_end=end,
                        target=timeline.track_id,
                        masker=None,
                        severity=0.45,
                        reason=f"{timeline.track_id} is narrow and may compete with centered VO.",
                        evidence={"stereo_width": frame.stereo_width},
                    )
                )
                issue_counter += 1

            if active_for_spatial and timeline.spatial_available and timeline.role in {"ambience"} and frame.distance_proxy is not None and frame.distance_proxy > 0.62:
                start, end = _issue_span(idx, timeline.frame_ms)
                issues.append(
                    Issue(
                        id=f"issue_{issue_counter}",
                        issue_type="foreground_ambience",
                        time_start=start,
                        time_end=end,
                        target=timeline.track_id,
                        masker=None,
                        severity=frame.distance_proxy,
                        reason=f"{timeline.track_id} ambience reads too close or forward for a background bed.",
                        evidence={
                            "distance_proxy": frame.distance_proxy,
                            "brightness_db": frame.brightness_db,
                            "stereo_width": frame.stereo_width,
                        },
                    )
                )
                issue_counter += 1

            if frame.clipping_risk or frame.peak_db > -0.5:
                start, end = _issue_span(idx, timeline.frame_ms)
                issues.append(
                    Issue(
                        id=f"issue_{issue_counter}",
                        issue_type="clipping_risk",
                        time_start=start,
                        time_end=end,
                        target=timeline.track_id,
                        masker=None,
                        severity=1.0,
                        reason=f"{timeline.track_id} peak is close to full scale.",
                        evidence={"peak_db": round(frame.peak_db, 2)},
                    )
                )
                issue_counter += 1

            low_avg = _band_avg(frame, LOW_BANDS)
            if low_avg > -16.0 and timeline.role in {"music", "ambience", "sfx", "background"}:
                start, end = _issue_span(idx, timeline.frame_ms)
                issues.append(
                    Issue(
                        id=f"issue_{issue_counter}",
                        issue_type="low_end_buildup",
                        time_start=start,
                        time_end=end,
                        target=timeline.track_id,
                        masker=None,
                        severity=min(1.0, (low_avg + 24.0) / 18.0),
                        reason=f"{timeline.track_id} has strong low-frequency energy.",
                        evidence={"low_band_avg_db": round(low_avg, 2)},
                    )
                )
                issue_counter += 1

    if by_id:
        frame_count = max(len(timeline.frames) for timeline in timelines)
        frame_ms = timelines[0].frame_ms
        for idx in range(frame_count):
            active = []
            for timeline in timelines:
                if idx < len(timeline.frames) and timeline.frames[idx].loudness_db > -28.0:
                    active.append(timeline.track_id)
            if len(active) >= 4:
                start, end = _issue_span(idx, frame_ms)
                issues.append(
                    Issue(
                        id=f"issue_{issue_counter}",
                        issue_type="bus_balance_imbalance",
                        time_start=start,
                        time_end=end,
                        target="mix",
                        masker=None,
                        severity=min(1.0, len(active) / 8.0),
                        reason="Many tracks are loud at the same time; review priority and bus balance.",
                        evidence={"active_tracks": active},
                    )
                )
                issue_counter += 1

    for target in dialogue_tracks:
        for masker in maskers:
            frame_count = min(len(target.frames), len(masker.frames))
            for idx in range(frame_count):
                target_frame = target.frames[idx]
                masker_frame = masker.frames[idx]
                if (
                    target_frame.loudness_db > -55
                    and masker.spatial_available
                    and masker_frame.distance_proxy is not None
                    and masker_frame.distance_proxy > 0.72
                    and masker_frame.loudness_db > -45
                    and masker.role in {"music", "ambience", "sfx", "background"}
                ):
                    start, end = _issue_span(idx, target.frame_ms)
                    issues.append(
                        Issue(
                            id=f"issue_{issue_counter}",
                            issue_type="depth_conflict",
                            time_start=start,
                            time_end=end,
                            target=target.track_id,
                            masker=masker.track_id,
                            severity=masker_frame.distance_proxy,
                            reason=f"{masker.track_id} reads too forward while {target.track_id} dialogue is active.",
                            evidence={
                                "masker_distance_proxy": masker_frame.distance_proxy,
                                "masker_width": masker_frame.stereo_width,
                                "target_loudness_db": target_frame.loudness_db,
                            },
                        )
                    )
                    issue_counter += 1

    return issues
