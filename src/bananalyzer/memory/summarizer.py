from dataclasses import dataclass
from datetime import datetime

from bananalyzer.memory.store import MemoryStore
from bananalyzer.events import emit_event


@dataclass
class MemoryUpdateResult:
    summary: str
    timestamp: str
    state: str
    skipped: bool


def should_skip_update(store: MemoryStore, last_summary_content: str, current_state: str) -> bool:
    if not last_summary_content.strip():
        return False

    if current_state not in last_summary_content:
        return False

    return True


def generate_session_summary(store: MemoryStore, current_state: str) -> MemoryUpdateResult:
    memory_content = store.read_memory()
    timestamp = datetime.now().isoformat()

    parts = []
    parts.append(f"Session state: {current_state}")

    if "## Goals" in memory_content:
        goals_start = memory_content.find("## Goals")
        goals_end = memory_content.find("\n## ", goals_start + 1)
        goals_section = memory_content[goals_start:goals_end].strip() if goals_end != -1 else memory_content[goals_start:].strip()
        if goals_section:
            parts.append(goals_section)

    if "## Mistakes" in memory_content:
        mistakes_start = memory_content.find("## Mistakes")
        mistakes_end = memory_content.find("\n## ", mistakes_start + 1)
        mistakes_section = memory_content[mistakes_start:mistakes_end].strip() if mistakes_end != -1 else memory_content[mistakes_start:].strip()
        if mistakes_section:
            parts.append(mistakes_section)

    if "## Progress" in memory_content:
        progress_start = memory_content.find("## Progress")
        progress_end = memory_content.find("\n## ", progress_start + 1)
        progress_section = memory_content[progress_start:progress_end].strip() if progress_end != -1 else memory_content[progress_start:].strip()
        if progress_section:
            parts.append(progress_section)

    summary = "\n\n".join(parts)

    store.update_session_summary(summary)

    emit_event(
        event_type="memory.updated",
        component="memory_summarizer",
        severity="info",
        message="Session memory updated",
        details={"state": current_state, "summary_length": len(summary)},
    )

    return MemoryUpdateResult(
        summary=summary,
        timestamp=timestamp,
        state=current_state,
        skipped=False,
    )


def periodic_memory_update(store: MemoryStore, current_state: str, last_summary: str) -> tuple[str, bool]:
    if should_skip_update(store, last_summary, current_state):
        emit_event(
            event_type="memory.skipped",
            component="memory_summarizer",
            severity="info",
            message="Memory update skipped - no meaningful changes",
            details={"state": current_state},
        )
        return last_summary, True

    result = generate_session_summary(store, current_state)
    return result.summary, result.skipped
