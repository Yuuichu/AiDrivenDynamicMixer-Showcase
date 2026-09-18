from __future__ import annotations

from core.schemas import Issue, MixRecommendation, MixSession


def recommend_actions(session: MixSession, issues: list[Issue]) -> list[MixRecommendation]:
    recommendations: list[MixRecommendation] = []
    for index, issue in enumerate(issues, start=1):
        operation = "marker_only_issue_annotation"
        amount: dict[str, object] = {}
        hint: dict[str, object] = {"host": session.host}

        if issue.issue_type == "dialogue_masking" and issue.masker:
            operation = "dynamic_eq_ducking"
            amount = {
                "band_hz": [1250, 5000],
                "gain_db": round(-1.5 - issue.severity * 2.5, 1),
                "attack_ms": 120,
                "release_ms": 700,
            }
            hint = {
                "reaper": "Map to an EQ band gain envelope on the masker track after human approval.",
                "wwise": "Map to Meter/RTPC-driven ducking or snapshot EQ on the masker bus after human approval.",
            }
            target = issue.masker
        elif issue.issue_type == "low_end_buildup":
            operation = "low_cut_cleanup_suggestion"
            amount = {"cutoff_hz": 80, "slope_db_per_oct": 12, "gain_db": -2.0}
            target = issue.target
        elif issue.issue_type == "clipping_risk":
            operation = "static_gain_adjustment"
            amount = {"gain_db": -2.0}
            target = issue.target
        elif issue.issue_type == "bus_balance_imbalance":
            operation = "volume_ducking"
            amount = {"gain_db": -1.5, "attack_ms": 250, "release_ms": 900}
            target = issue.target
        elif issue.issue_type == "foreground_ambience":
            operation = "spatial_reposition_suggestion"
            amount = {"move_back": True, "mid_high_duck_db": -2.0, "reduce_directness": True}
            target = issue.target
        elif issue.issue_type == "overwide_dialogue":
            operation = "stereo_width_adjustment"
            amount = {"target_width": "narrow_to_medium", "center_focus": True}
            target = issue.target
        elif issue.issue_type == "narrow_music_field":
            operation = "stereo_width_adjustment"
            amount = {"target_width": "medium_wide", "protect_center_voice": True}
            target = issue.target
        elif issue.issue_type == "phase_risk":
            operation = "mid_side_cleanup"
            amount = {"check_mono_compatibility": True, "reduce_side_or_fix_phase": True}
            target = issue.target
        elif issue.issue_type == "depth_conflict":
            operation = "depth_rebalance"
            amount = {"move_masker_back": True, "duck_direct_component_db": -2.0}
            target = issue.masker or issue.target
        else:
            target = issue.target

        recommendations.append(
            MixRecommendation(
                id=f"rec_{index}",
                issue_id=issue.id,
                time_start=issue.time_start,
                time_end=issue.time_end,
                target=target,
                operation=operation,
                suggested_amount=amount,
                confidence=round(max(0.35, min(0.9, issue.severity * 0.85)), 2),
                reason=issue.reason,
                requires_human_review=True,
                host_mapping_hint=hint,
            )
        )
    return recommendations
