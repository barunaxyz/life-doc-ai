import json

from openai import OpenAI

from agent.prompts import (
    CHAPTERS_PROMPT,
    DOCUMENTARY_PROMPT,
    INSIGHT_PROMPT,
    TIMELINE_PROMPT,
)
from config import OPENAI_API_KEY
from mcp.notion_client import get_goals, get_journal_entries, get_life_events
from services.chapter_service import generate_chapters
from services.insight_service import extract_insights
from services.timeline_service import build_timeline


class DocumentaryAgent:
    def __init__(self):
        if OPENAI_API_KEY and "your_openai" not in OPENAI_API_KEY:
            self.client = OpenAI(api_key=OPENAI_API_KEY)
        else:
            self.client = None

    def _call_llm(self, system_prompt, user_data, max_tokens=1000):
        """Call the LLM or generate a rule-based narrative if no API key."""
        if not self.client:
            # Generate a simple narrative from the actual data (no mock text)
            return self._generate_fallback(system_prompt, user_data)

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": f"Here is the data: {json.dumps(user_data)}",
                    },
                ],
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"LLM Error: {e}")
            return self._generate_fallback(system_prompt, user_data)

    def _generate_fallback(self, system_prompt, user_data):
        """Build a narrative directly from the data without an LLM."""
        events = user_data.get("events", [])
        journals = user_data.get("journals", [])

        if not events and not journals:
            return "*No data available. Please connect your Notion databases first.*"

        prompt_type = system_prompt.lower()

        if "story" in prompt_type:
            return self._fallback_story(events, journals)
        elif "timeline" in prompt_type:
            return self._fallback_timeline(events)
        elif "chapter" in prompt_type:
            return self._fallback_chapters(events)
        else:
            return self._fallback_insights(events, journals)

    @staticmethod
    def _fmt_date(raw_date):
        """Format a raw date string (YYYY-MM-DD) into a readable form."""
        MONTHS = [
            "",
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December",
        ]
        try:
            parts = raw_date.split("-")
            y, m, d = parts[0], int(parts[1]), int(parts[2])
            return f"{MONTHS[m]} {d}, {y}"
        except Exception:
            return raw_date or "an unknown date"

    def _fallback_story(self, events, journals):
        """Create a rich HTML story from events and journals."""
        html = ""
        if events:
            sorted_events = sorted(events, key=lambda e: e.get("date", ""))
            first = sorted_events[0]
            last = sorted_events[-1]

            # Opening paragraph
            html += (
                f'<p style="font-size:1.05rem;line-height:1.9;color:#CBD5E1;margin-bottom:1.4rem;">'
                f"Every great story has a beginning. Yours started on "
                f'<strong style="color:#A78BFA;">{self._fmt_date(first.get("date", ""))}</strong>, '
                f"when you took a bold step and "
                f'<strong style="color:#F1F5F9;">{first.get("event", "started your path").lower()}</strong>. '
                f"That single decision set the course for everything that followed.</p>"
            )

            # Middle events — the journey
            if len(sorted_events) > 2:
                html += (
                    '<p style="font-size:1.05rem;line-height:1.9;color:#CBD5E1;margin-bottom:1.4rem;">'
                    "From there, your path was anything but ordinary. "
                )
                mid_events = sorted_events[1:-1]
                highlights = mid_events[:4]  # Show up to 4 middle events
                for i, ev in enumerate(highlights):
                    name = ev.get("event", "").lower()
                    date = self._fmt_date(ev.get("date", ""))
                    if i == 0:
                        html += f'In <strong style="color:#A78BFA;">{date}</strong>, you <strong style="color:#F1F5F9;">{name}</strong>. '
                    elif i == len(highlights) - 1:
                        html += f'And by <strong style="color:#A78BFA;">{date}</strong>, you had <strong style="color:#F1F5F9;">{name}</strong>. '
                    else:
                        html += f'Then in <strong style="color:#A78BFA;">{date}</strong>, you <strong style="color:#F1F5F9;">{name}</strong>. '
                html += "</p>"

            # Latest event
            html += (
                f'<p style="font-size:1.05rem;line-height:1.9;color:#CBD5E1;margin-bottom:1.4rem;">'
                f"Most recently, on "
                f'<strong style="color:#A78BFA;">{self._fmt_date(last.get("date", ""))}</strong>, '
                f'you <strong style="color:#F1F5F9;">{last.get("event", "continued evolving").lower()}</strong> '
                f"— a testament to your ever-growing curiosity and drive.</p>"
            )

            # High-impact highlights
            high_impact = [e for e in sorted_events if e.get("impact") == "High"]
            if high_impact:
                html += (
                    '<p style="font-size:1.05rem;line-height:1.9;color:#CBD5E1;margin-bottom:1.4rem;">'
                    f'Across your journey, <strong style="color:#EC4899;">{len(high_impact)} defining moments</strong> '
                    f"stand out as high-impact turning points that shaped who you are today.</p>"
                )

        # Journal excerpts
        if journals:
            html += (
                f'<div style="margin-top:1.8rem;margin-bottom:1rem;">'
                f'<p style="font-size:0.85rem;text-transform:uppercase;letter-spacing:1.5px;'
                f'color:#7C3AED;font-weight:600;margin-bottom:1rem;">📓 From Your Journal — {len(journals)} Entries</p>'
            )
            sorted_journals = sorted(journals, key=lambda j: j.get("date", ""))
            for j in sorted_journals[:4]:
                content = j.get("content", "")
                if len(content) > 160:
                    content = content[:160] + "…"
                date = self._fmt_date(j.get("date", ""))
                html += (
                    f'<div style="border-left:3px solid #7C3AED;padding:12px 16px;margin-bottom:12px;'
                    f'background:rgba(124,58,237,0.06);border-radius:0 10px 10px 0;">'
                    f'<p style="color:#E2E8F0;font-style:italic;margin:0 0 6px 0;line-height:1.7;">"{content}"</p>'
                    f'<p style="color:#7C3AED;font-size:0.8rem;margin:0;font-weight:500;">— {date}</p>'
                    f"</div>"
                )
            html += "</div>"

        return html

    def _fallback_timeline(self, events):
        """Create an HTML timeline from events."""
        if not events:
            return '<p style="color:#94A3B8;">No events to display.</p>'
        sorted_events = sorted(events, key=lambda e: e.get("date", ""))
        html = ""
        for ev in sorted_events:
            impact = ev.get("impact", "")
            if impact == "High":
                dot_color = "#EF4444"
                badge = '<span style="font-size:0.7rem;background:rgba(239,68,68,0.15);color:#EF4444;padding:2px 8px;border-radius:6px;margin-left:10px;font-weight:600;">HIGH IMPACT</span>'
            elif impact == "Medium":
                dot_color = "#F59E0B"
                badge = '<span style="font-size:0.7rem;background:rgba(245,158,11,0.15);color:#F59E0B;padding:2px 8px;border-radius:6px;margin-left:10px;font-weight:600;">MEDIUM</span>'
            else:
                dot_color = "#06B6D4"
                badge = ""

            date = self._fmt_date(ev.get("date", ""))
            html += (
                f'<div style="display:flex;align-items:flex-start;gap:14px;margin-bottom:18px;">'
                f'<div style="min-width:10px;padding-top:6px;">'
                f'<div style="width:10px;height:10px;border-radius:50%;background:{dot_color};'
                f'box-shadow:0 0 8px {dot_color}55;"></div></div>'
                f"<div>"
                f'<span style="color:#A78BFA;font-weight:600;font-size:0.85rem;">{date}</span>{badge}'
                f'<p style="color:#E2E8F0;margin:4px 0 0 0;line-height:1.6;">{ev.get("event", "")}</p>'
                f"</div></div>"
            )
        return html

    def _fallback_chapters(self, events):
        """Group events into HTML chapters by year."""
        if not events:
            return '<p style="color:#94A3B8;">No events to organize into chapters.</p>'
        sorted_events = sorted(events, key=lambda e: e.get("date", ""))
        years = {}
        for ev in sorted_events:
            year = ev.get("date", "????")[:4]
            years.setdefault(year, []).append(ev)

        chapter_names = [
            "The Beginning",
            "Building Foundations",
            "Rising Momentum",
            "The Breakthrough",
            "New Horizons",
            "The Next Chapter",
        ]
        html = ""
        for i, (year, evts) in enumerate(years.items()):
            name = chapter_names[i] if i < len(chapter_names) else f"Era {i + 1}"
            colors = ["#7C3AED", "#EC4899", "#06B6D4", "#F59E0B", "#10B981", "#8B5CF6"]
            color = colors[i % len(colors)]
            html += (
                f'<div style="background:linear-gradient(135deg,{color}11,{color}05);'
                f"border-left:3px solid {color};border-radius:0 14px 14px 0;"
                f'padding:18px 20px;margin-bottom:16px;">'
                f'<div style="display:flex;align-items:center;gap:10px;margin-bottom:10px;">'
                f'<span style="font-size:0.75rem;background:{color}22;color:{color};'
                f'padding:3px 10px;border-radius:6px;font-weight:700;">CHAPTER {i + 1}</span>'
                f'<span style="color:#F1F5F9;font-weight:700;font-size:1.1rem;">{name}</span>'
                f'<span style="color:#64748B;font-size:0.85rem;">({year})</span></div>'
            )
            for ev in evts:
                html += (
                    f'<p style="color:#CBD5E1;margin:6px 0 6px 12px;line-height:1.6;">'
                    f"→ {ev.get('event', '')}"
                    f'<span style="color:#64748B;font-size:0.82rem;"> — {self._fmt_date(ev.get("date", ""))}</span></p>'
                )
            html += "</div>"
        return html

    def _fallback_insights(self, events, journals):
        """Extract styled HTML insights from the data."""
        items = []
        if events:
            years = [e.get("date", "")[:4] for e in events if e.get("date")]
            if years:
                from collections import Counter

                most_active = Counter(years).most_common(1)[0]
                items.append(
                    (
                        "📅",
                        "Most Active Year",
                        f"{most_active[0]} with {most_active[1]} events",
                        "#7C3AED",
                    )
                )

            high_impact = [e for e in events if e.get("impact") == "High"]
            pct = round(len(high_impact) / len(events) * 100)
            items.append(
                (
                    "🔴",
                    "High-Impact Events",
                    f"{len(high_impact)} out of {len(events)} ({pct}%)",
                    "#EF4444",
                )
            )

            first_year = min(years) if years else "?"
            last_year = max(years) if years else "?"
            span = int(last_year) - int(first_year) + 1 if years else 0
            items.append(
                (
                    "📊",
                    "Journey Span",
                    f"{span} years ({first_year} — {last_year})",
                    "#06B6D4",
                )
            )

        if journals:
            items.append(
                (
                    "📓",
                    "Journal Entries",
                    f"{len(journals)} reflections documented",
                    "#EC4899",
                )
            )
            avg_len = sum(len(j.get("content", "")) for j in journals) // max(
                len(journals), 1
            )
            items.append(
                (
                    "✍️",
                    "Avg. Entry Length",
                    f"~{avg_len} characters per entry",
                    "#F59E0B",
                )
            )

        if not items:
            return '<p style="color:#94A3B8;">No data available for insights.</p>'

        html = '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px;">'
        for emoji, label, value, color in items:
            html += (
                f'<div style="background:linear-gradient(135deg,{color}11,{color}05);'
                f'border:1px solid {color}22;border-radius:14px;padding:16px 18px;">'
                f'<div style="font-size:1.4rem;margin-bottom:6px;">{emoji}</div>'
                f'<div style="color:{color};font-weight:700;font-size:0.95rem;margin-bottom:4px;">{label}</div>'
                f'<div style="color:#CBD5E1;font-size:0.9rem;">{value}</div>'
                f"</div>"
            )
        html += "</div>"
        return html

    def generate_documentary(self):
        """
        Main orchestration function:
        1. Fetch data from Notion MCP Tools
        2. Process with Services or LLM
        3. Return structural components
        """
        print("Gathering data from Notion...")
        events = get_life_events()
        journals = get_journal_entries()
        goals = get_goals()

        print(
            f"  → Found {len(events)} events, {len(journals)} journals, {len(goals)} goals"
        )

        bundle = {
            "events": events,
            "journals": journals,
            "goals": goals,
        }

        print("Generating Timeline...")
        ai_timeline = self._call_llm(TIMELINE_PROMPT, bundle, 500)
        base_timeline = build_timeline(events)

        print("Generating Chapters...")
        ai_chapters = self._call_llm(CHAPTERS_PROMPT, bundle, 500)
        base_chapters = generate_chapters(base_timeline, journals)

        print("Generating Insights...")
        ai_insights = self._call_llm(INSIGHT_PROMPT, bundle, 500)
        base_insights = extract_insights(events, journals)

        print("Writing the final Narrative Story...")
        story = self._call_llm(DOCUMENTARY_PROMPT, bundle, 2000)

        return {
            "timeline": base_timeline,
            "ai_timeline": ai_timeline,
            "chapters": base_chapters,
            "ai_chapters": ai_chapters,
            "insights": base_insights,
            "ai_insights": ai_insights,
            "story": story,
        }
