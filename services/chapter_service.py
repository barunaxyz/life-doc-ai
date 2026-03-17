def generate_chapters(timeline_data, journal_entries):
    """
    Groups timeline data and journals into chapters.
    In a full implementation, this might call an LLM to smartly categorize eras.
    """
    if not timeline_data:
        return []
        
    # Example logic: just divide events into groups of 3
    chapters = []
    chunk_size = max(1, len(timeline_data) // 3)
    
    for i in range(0, len(timeline_data), chunk_size):
        chunk = timeline_data[i:i+chunk_size]
        chapter_title = f"Chapter {(i//chunk_size)+1} — The {chunk[0].split('—')[0].strip()} Era"
        chapters.append(chapter_title)
        
    return chapters
