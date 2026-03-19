def extract_insights(events, journals):
    """
    Extract meaningful insights from events and journals.
    Like finding the most active year, core themes, etc.
    """
    if not events and not journals:
        return []

    # Dummy logic to illustrate analysis
    years = [str(ev.get("date", "")).split("-")[0] for ev in events if ev.get("date")]
    most_active_year = max(set(years), key=years.count) if years else "Unknown"

    return [
        f"Most active year: {most_active_year}",
        "Most emotional events: reflected in journals",
        f"Core theme based on {len(journals)} journal entries collected.",
    ]
