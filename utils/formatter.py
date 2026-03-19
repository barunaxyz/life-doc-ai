import html


def _escape(text):
    """Safely escape text for HTML output."""
    return html.escape(str(text))


def format_timeline(timeline_data):
    """
    Format timeline data into styled HTML list items.
    """
    if not timeline_data:
        return "<p>No timeline available.</p>"

    items = ""
    for item in timeline_data:
        parts = str(item).split("—", 1)
        if len(parts) == 2:
            year = _escape(parts[0].strip())
            desc = _escape(parts[1].strip())
            items += (
                f'<div style="display:flex;align-items:baseline;gap:12px;margin-bottom:14px;">'
                f'<span style="font-weight:700;font-size:1.1rem;'
                f"background:linear-gradient(135deg,#7C3AED,#EC4899);"
                f"-webkit-background-clip:text;-webkit-text-fill-color:transparent;"
                f'white-space:nowrap;">{year}</span>'
                f'<span style="color:#CBD5E1;">{desc}</span>'
                f"</div>"
            )
        else:
            items += (
                f'<p style="color:#CBD5E1;margin-bottom:10px;">• {_escape(item)}</p>'
            )

    return items


def format_chapters(chapters_data):
    """
    Format chapters data into styled HTML.
    """
    if not chapters_data:
        return "<p>No chapters available.</p>"

    items = ""
    for idx, item in enumerate(chapters_data, 1):
        title = _escape(str(item))
        items += (
            f'<div style="background:linear-gradient(135deg,rgba(124,58,237,0.08),rgba(236,72,153,0.04));'
            f"border-left:3px solid #7C3AED;border-radius:0 12px 12px 0;"
            f'padding:14px 18px;margin-bottom:12px;">'
            f'<span style="color:#F1F5F9;font-weight:600;">{title}</span>'
            f"</div>"
        )

    return items


def format_story(story_text):
    """
    Format story text into clean HTML paragraphs.
    If content is already HTML (from fallback), pass through as-is.
    """
    if not story_text:
        return "<p>No story available.</p>"

    text = str(story_text)

    # If already HTML (from fallback generators), pass through
    if "<p " in text or "<div " in text or "<strong " in text:
        return text

    # Convert markdown-like text (from LLM) to HTML paragraphs
    paragraphs = text.split("\n\n")
    formatted = ""
    for para in paragraphs:
        clean = para.strip()
        if clean:
            # Convert markdown bold to HTML bold
            while "**" in clean:
                clean = clean.replace("**", "<strong style='color:#F1F5F9;'>", 1)
                if "**" in clean:
                    clean = clean.replace("**", "</strong>", 1)
            # Convert markdown italic
            while "*" in clean:
                clean = clean.replace("*", "<em>", 1)
                if "*" in clean:
                    clean = clean.replace("*", "</em>", 1)
            formatted += f'<p style="color:#CBD5E1;margin-bottom:1.1rem;line-height:1.85;">{clean}</p>'

    return formatted


def format_insights(insights_data):
    """
    Format insights into styled numbered cards.
    """
    if not insights_data:
        return "<p>No insights available.</p>"

    colors = ["#7C3AED", "#EC4899", "#06B6D4", "#F59E0B", "#10B981"]

    items = ""
    for idx, insight in enumerate(insights_data):
        color = colors[idx % len(colors)]
        text = _escape(str(insight))
        items += (
            f'<div style="display:flex;align-items:center;gap:14px;margin-bottom:14px;">'
            f'<div style="min-width:36px;height:36px;border-radius:10px;'
            f"background:linear-gradient(135deg,{color}33,{color}11);"
            f"display:flex;align-items:center;justify-content:center;"
            f'font-weight:700;font-size:0.9rem;color:{color};">{idx + 1}</div>'
            f'<span style="color:#CBD5E1;">{text}</span>'
            f"</div>"
        )

    return items
