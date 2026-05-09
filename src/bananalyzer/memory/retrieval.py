from bananalyzer.memory.store import MemoryStore

DEFAULT_MAX_MEMORY_CHARS = 1000


def truncate_memory_context(text: str | None, max_chars: int = DEFAULT_MAX_MEMORY_CHARS) -> str:
    if not text:
        return ""

    if len(text) <= max_chars:
        return text

    truncated = text[:max_chars].rstrip()
    return f"{truncated}\n\n...(memory truncated to {max_chars} chars)"


def retrieve_memory_context(
    store: MemoryStore,
    current_state: str,
    max_chars: int = DEFAULT_MAX_MEMORY_CHARS,
) -> str:
    parts = []

    try:
        memory_content = store.read_memory()
    except Exception:
        memory_content = ""

    try:
        session_content = store.read_session_summary()
    except Exception:
        session_content = ""

    if "## Goals" in memory_content:
        goals_start = memory_content.find("## Goals")
        goals_end = memory_content.find("\n## ", goals_start + 1)
        goals_section = memory_content[goals_start:goals_end].strip() if goals_end != -1 else memory_content[goals_start:].strip()
        if goals_section and goals_section != "## Goals":
            parts.append(goals_section)

    if "## Mistakes" in memory_content:
        mistakes_start = memory_content.find("## Mistakes")
        mistakes_end = memory_content.find("\n## ", mistakes_start + 1)
        mistakes_section = memory_content[mistakes_start:mistakes_end].strip() if mistakes_end != -1 else memory_content[mistakes_start:].strip()
        if mistakes_section and mistakes_section != "## Mistakes":
            parts.append(mistakes_section)

    if "## Progress" in memory_content:
        progress_start = memory_content.find("## Progress")
        progress_end = memory_content.find("\n## ", progress_start + 1)
        progress_section = memory_content[progress_start:progress_end].strip() if progress_end != -1 else memory_content[progress_start:].strip()
        if progress_section and progress_section != "## Progress":
            parts.append(progress_section)

    if session_content.strip() and session_content.strip() != "# Session Summary":
        parts.append(session_content.strip())

    combined = "\n\n".join(parts)
    return truncate_memory_context(combined, max_chars=max_chars)


def get_memory_prompt_block(
    store: MemoryStore | None,
    current_state: str,
    max_chars: int = DEFAULT_MAX_MEMORY_CHARS,
) -> str:
    if store is None:
        return ""

    if not store.available:
        return ""

    try:
        context = retrieve_memory_context(store, current_state, max_chars=max_chars)
    except Exception:
        return ""

    if not context.strip():
        return ""

    return f"## Memory Context\n\nThe following is relevant context from previous sessions:\n\n{context}"
