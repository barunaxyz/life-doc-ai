def build_timeline(events):
    """
    Process raw Notion events into a timeline structure.
    This can be used before sending to AI or after AI generation.
    """
    timeline = []
    
    if not events:
        return []
        
    for event in events:
        # Simplistic parsing, assumes dict with "date" and "event" keys
        date = event.get("date", "Unknown Date")
        year = date.split("-")[0] if "-" in date else date
        desc = event.get("event", "Unknown Event")
        timeline.append(f"{year} — {desc}")
        
    return sorted(timeline) # Sort chronologically conceptually
