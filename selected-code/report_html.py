from __future__ import annotations

import html
import json

from core.schemas import Issue, MixRecommendation, MixSession, TrackFeatureTimeline


def _fmt_time(seconds: float) -> str:
    minutes = int(seconds // 60)
    remainder = seconds - minutes * 60
    return f"{minutes:02d}:{remainder:06.3f}"


def render_html_report(
    session: MixSession,
    features: list[TrackFeatureTimeline],
    issues: list[Issue],
    recommendations: list[MixRecommendation],
) -> str:
    track_rows = "\n".join(
        f"<tr><td>{html.escape(track.id)}</td><td>{html.escape(track.name)}</td><td>{html.escape(track.role)}</td><td>{html.escape(track.source)}</td></tr>"
        for track in session.tracks
    )
    issue_rows = "\n".join(
        "<tr>"
        f"<td>{html.escape(issue.id)}</td>"
        f"<td>{html.escape(issue.issue_type)}</td>"
        f"<td>{_fmt_time(issue.time_start)} - {_fmt_time(issue.time_end)}</td>"
        f"<td>{html.escape(issue.target)}</td>"
        f"<td>{html.escape(issue.masker or '')}</td>"
        f"<td>{issue.severity:.2f}</td>"
        f"<td>{html.escape(issue.reason)}</td>"
        "</tr>"
        for issue in issues
    )
    rec_rows = "\n".join(
        "<tr>"
        f"<td>{html.escape(rec.id)}</td>"
        f"<td>{html.escape(rec.operation)}</td>"
        f"<td>{_fmt_time(rec.time_start)} - {_fmt_time(rec.time_end)}</td>"
        f"<td>{html.escape(rec.target)}</td>"
        f"<td>{html.escape(json.dumps(rec.suggested_amount, ensure_ascii=False))}</td>"
        f"<td>{rec.confidence:.2f}</td>"
        f"<td>{'yes' if rec.requires_human_review else 'no'}</td>"
        "</tr>"
        for rec in recommendations
    )
    feature_summary = "\n".join(
        f"<li>{html.escape(timeline.track_id)}: {len(timeline.frames)} frames, role={html.escape(timeline.role)}</li>"
        for timeline in features
    )
    spatial_rows = "\n".join(
        "<tr>"
        f"<td>{html.escape(timeline.track_id)}</td>"
        f"<td>{html.escape(timeline.role)}</td>"
        f"<td>{timeline.channel_count}</td>"
        f"<td>{_avg_spatial(timeline, 'pan_estimate')}</td>"
        f"<td>{_avg_spatial(timeline, 'stereo_width')}</td>"
        f"<td>{_avg_spatial(timeline, 'lr_correlation')}</td>"
        f"<td>{_avg_spatial(timeline, 'distance_proxy')}</td>"
        "</tr>"
        for timeline in features
    )
    spatial_issue_rows = "\n".join(
        "<tr>"
        f"<td>{html.escape(issue.issue_type)}</td>"
        f"<td>{_fmt_time(issue.time_start)} - {_fmt_time(issue.time_end)}</td>"
        f"<td>{html.escape(issue.target)}</td>"
        f"<td>{html.escape(issue.masker or '')}</td>"
        f"<td>{issue.severity:.2f}</td>"
        f"<td>{html.escape(issue.reason)}</td>"
        "</tr>"
        for issue in issues
        if issue.issue_type in {"foreground_ambience", "overwide_dialogue", "narrow_music_field", "phase_risk", "depth_conflict"}
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>AiDrivenDynamicMixer Report</title>
  <style>
    body {{ font-family: Segoe UI, Arial, sans-serif; margin: 32px; color: #1f2933; }}
    h1, h2 {{ margin: 0 0 12px; }}
    section {{ margin: 28px 0; }}
    table {{ border-collapse: collapse; width: 100%; font-size: 14px; }}
    th, td {{ border: 1px solid #d8dee9; padding: 8px; vertical-align: top; }}
    th {{ background: #eef2f7; text-align: left; }}
    code {{ background: #eef2f7; padding: 2px 4px; }}
  </style>
</head>
<body>
  <h1>AiDrivenDynamicMixer Report</h1>
  <p>Host: <code>{html.escape(session.host)}</code> | Duration: {session.duration_seconds:.2f}s | Frame: {session.frame_ms}ms</p>

  <section>
    <h2>Tracks / Buses</h2>
    <table><thead><tr><th>ID</th><th>Name</th><th>Role</th><th>Source</th></tr></thead><tbody>{track_rows}</tbody></table>
  </section>

  <section>
    <h2>Feature Summary</h2>
    <ul>{feature_summary}</ul>
  </section>

  <section>
    <h2>Spatial Summary</h2>
    <p>Distance is a proxy, not an absolute physical distance. Use it as a mix review hint.</p>
    <table><thead><tr><th>ID</th><th>Role</th><th>Channels</th><th>Avg Pan</th><th>Avg Width</th><th>Avg L/R Correlation</th><th>Avg Distance Proxy</th></tr></thead><tbody>{spatial_rows}</tbody></table>
  </section>

  <section>
    <h2>Spatial Risks</h2>
    <table><thead><tr><th>Type</th><th>Time</th><th>Target</th><th>Masker</th><th>Severity</th><th>Reason</th></tr></thead><tbody>{spatial_issue_rows}</tbody></table>
  </section>

  <section>
    <h2>Issues</h2>
    <table><thead><tr><th>ID</th><th>Type</th><th>Time</th><th>Target</th><th>Masker</th><th>Severity</th><th>Reason</th></tr></thead><tbody>{issue_rows}</tbody></table>
  </section>

  <section>
    <h2>Recommendations</h2>
    <table><thead><tr><th>ID</th><th>Operation</th><th>Time</th><th>Target</th><th>Suggested Amount</th><th>Confidence</th><th>Human Review</th></tr></thead><tbody>{rec_rows}</tbody></table>
  </section>
</body>
</html>
"""


def _avg_spatial(timeline: TrackFeatureTimeline, attr: str) -> str:
    values = [getattr(frame, attr) for frame in timeline.frames if getattr(frame, attr) is not None]
    if not values:
        return "n/a"
    return f"{sum(values) / len(values):.3f}"
