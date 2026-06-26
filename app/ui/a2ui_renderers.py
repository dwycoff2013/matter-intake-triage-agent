"""HTML renderers for A2UI-style LexTriage payloads."""

from __future__ import annotations

from html import escape


def _items_html(items: list[str]) -> str:
    return "".join(f"<li>{escape(str(item))}</li>" for item in items)


def render_a2ui_payload_html(payload: dict) -> str:
    """Render a validated A2UI-style intake payload as a standalone HTML panel."""

    case_id = escape(str(payload.get("case_id", "CASE-UNKNOWN")))
    title = escape(str(payload.get("title", "LexTriage Intake Review")))
    privacy_note = escape(
        str(payload.get("privacy_note", "Redacted/minimized preview for human review."))
    )
    review_class = (
        "requires-review" if payload.get("human_review_required") else "standard-review"
    )
    parts = [
        '<section class="lextriage-a2ui-panel">',
        f'<header><p class="eyebrow">{case_id}</p><h2>{title}</h2>',
        f'<p class="privacy-note">{privacy_note}</p></header>',
        f'<div class="review-state {review_class}">{"Human review required" if payload.get("human_review_required") else "Standard intake review"}</div>',
    ]
    for component in payload.get("components", []):
        if not isinstance(component, dict):
            continue
        ctype = component.get("type", "component")
        parts.append(f'<article class="component component-{escape(str(ctype))}">')
        parts.append(f'<h3>{escape(str(ctype).replace("_", " ").title())}</h3>')
        if "summary" in component:
            parts.append(f'<p>{escape(str(component["summary"]))}</p>')
        if "message" in component:
            parts.append(f'<p>{escape(str(component["message"]))}</p>')
        if "text" in component:
            parts.append(f'<p>{escape(str(component["text"]))}</p>')
        metadata = {
            k: v
            for k, v in component.items()
            if k not in {"type", "summary", "message", "text", "items", "flags"}
        }
        if metadata:
            rows = "".join(
                f'<tr><th>{escape(str(k).replace("_", " ").title())}</th><td>{escape(str(v))}</td></tr>'
                for k, v in metadata.items()
            )
            parts.append(f"<table>{rows}</table>")
        if component.get("flags"):
            parts.append(
                f'<p><strong>Flags:</strong> {escape(", ".join(map(str, component["flags"])))} </p>'
            )
        if component.get("items"):
            parts.append(f'<ul>{_items_html(component["items"])}</ul>')
        parts.append("</article>")
    parts.append("</section>")
    return "\n".join(parts)
