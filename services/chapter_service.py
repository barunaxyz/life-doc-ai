def generate_chapters(timeline_data, journal_entries):
    """
    Groups timeline data and journals into chapters.
    In a full implementation, this might call an LLM to smartly categorize eras.
    """
    if not timeline_data:
        return []

    from collections import defaultdict
    chapters_by_year = defaultdict(list)
    
    # Group events by year
    for item in timeline_data:
        try:
            year = item.split("—")[0].strip()[:4]
            if year.isdigit():
                chapters_by_year[year].append(item)
        except Exception:
            pass

    chapters = []
    chapter_num = 1
    
    for year, events in sorted(chapters_by_year.items()):
        # Try to find a high-impact event for the chapter headline, else take the first one
        prominent_event = events[-1] if events else ""
        for ev in events:
            if "(High)" in ev or "(high)" in ev:
                prominent_event = ev
                break
                
        try:
            parts = prominent_event.split("—", 1)
            event_name = parts[1].split("(")[0].strip()
            chapter_title = f"Chapter {chapter_num} ({year}) — Defining Milestone: '{event_name}'"
        except Exception:
            chapter_title = f"Chapter {chapter_num} — The {year} Era"
            
        chapters.append(chapter_title)
        chapter_num += 1

    return chapters
