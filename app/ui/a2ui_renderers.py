"""Notebook-friendly HTML renderers for A2UI-style payloads."""

from __future__ import annotations

import html
import json


def _esc(value: object) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def _render_items(items: object) -> str:
    if not isinstance(items, list):
        return ""
    return "".join(f'<li><label><input type="checkbox" disabled> {_esc(item)}</label></li>' for item in items)


def render_a2ui_payload_html(payload: dict) -> str:
    """Render a self-contained A2UI-style intake review panel for notebooks."""

    case_id = _esc(payload.get("case_id", "CASE-UNKNOWN"))
    human_review = bool(payload.get("human_review_required"))
    components_html: list[str] = []
    for component in payload.get("components", []):
        if not isinstance(component, dict):
            components_html.append(f"<pre>{_esc(json.dumps(component, sort_keys=True))}</pre>")
            continue
        ctype = component.get("type")
        if ctype == "risk_banner":
            components_html.append(f'<section class="risk"><strong>{_esc(component.get("severity", "review")).upper()}</strong><p>{_esc(component.get("message"))}</p></section>')
        elif ctype == "matter_summary_card":
            components_html.append(f'<section class="card"><h3>Matter Summary</h3><dl><dt>Area</dt><dd>{_esc(component.get("matter_area"))}</dd><dt>Subtype</dt><dd>{_esc(component.get("matter_subtype"))}</dd><dt>Urgency</dt><dd>{_esc(component.get("urgency"))}</dd></dl><p>{_esc(component.get("summary"))}</p></section>')
        elif ctype == "deadline_timeline":
            components_html.append(f'<section class="card"><h3>Deadline Timeline</h3><p><strong>Date:</strong> {_esc(component.get("deadline_date") or "Not provided")}</p><p><strong>Urgency:</strong> {_esc(component.get("urgency"))}</p><p><strong>Uncertainty:</strong> {_esc(component.get("uncertainty"))}</p></section>')
        elif ctype == "safety_flags":
            flags = component.get("flags") if isinstance(component.get("flags"), list) else []
            flags_html = "".join(f"<li>{_esc(flag)}</li>" for flag in flags) or "<li>None indicated</li>"
            components_html.append(f'<section class="card"><h3>Safety Flags</h3><ul>{flags_html}</ul><p>Human review required: {_esc(component.get("human_review_required"))}</p></section>')
        elif ctype == "missing_information_checklist":
            components_html.append(f'<section class="card"><h3>Missing Information Checklist</h3><ul class="checklist">{_render_items(component.get("items"))}</ul></section>')
        elif ctype == "recommended_next_actions":
            components_html.append(f'<section class="card"><h3>Recommended Next Actions</h3><ul class="checklist">{_render_items(component.get("items"))}</ul></section>')
        elif ctype == "human_review_disclaimer":
            components_html.append(f'<section class="disclaimer"><h3>Human Review Disclaimer</h3><p>{_esc(component.get("text"))}</p></section>')
        else:
            components_html.append(f'<section class="card"><h3>Unknown Component</h3><pre>{_esc(json.dumps(component, sort_keys=True))}</pre></section>')
    status = "Human review required" if human_review else "Automation-assisted review"
    return f'''<div class="lextriage-a2ui"><style>.lextriage-a2ui{{font-family:Arial,sans-serif;border:1px solid #cbd5e1;border-radius:14px;padding:18px;max-width:900px;background:#f8fafc;color:#0f172a}}.lextriage-a2ui header{{border-bottom:1px solid #e2e8f0;margin-bottom:12px}}.lextriage-a2ui .status{{display:inline-block;padding:4px 10px;border-radius:999px;background:{'#fee2e2' if human_review else '#dcfce7'};color:{'#991b1b' if human_review else '#166534'};font-weight:700}}.lextriage-a2ui .card,.lextriage-a2ui .risk,.lextriage-a2ui .disclaimer{{background:white;border:1px solid #e2e8f0;border-radius:12px;margin:10px 0;padding:14px;box-shadow:0 1px 2px rgba(15,23,42,.06)}}.lextriage-a2ui .risk{{border-left:6px solid #dc2626;background:#fff7ed}}.lextriage-a2ui .disclaimer{{border-left:6px solid #2563eb}}.lextriage-a2ui dt{{font-weight:700;float:left;clear:left;width:90px}}.lextriage-a2ui dd{{margin-left:110px}}.lextriage-a2ui .checklist{{list-style:none;padding-left:0}}.lextriage-a2ui input{{margin-right:8px}}</style><header><h2>{_esc(payload.get('title', 'LexTriage Intake Review'))}</h2><p>Case <strong>{case_id}</strong> <span class="status">{_esc(status)}</span></p><p><em>{_esc(payload.get('privacy_note', ''))}</em></p></header>{''.join(components_html)}</div>'''
