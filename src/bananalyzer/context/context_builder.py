from __future__ import annotations

from typing import Any

from bananalyzer.config import load_settings_safe
from bananalyzer.context.code_context import BoundedCodeContext, bound_text


def _extract_text_field(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        text = value.get("text")
        if isinstance(text, str):
            return text
    return None


def _choose_source_text(data: dict[str, Any]) -> tuple[str | None, str | None]:
    selection_text = _extract_text_field(data.get("selection"))
    if selection_text:
        return selection_text, "selection"

    visible_text = _extract_text_field(data.get("visible"))
    if visible_text:
        return visible_text, "visible"

    content_text = _extract_text_field(data.get("content"))
    if content_text:
        return content_text, "content"

    return None, None


def build_bounded_coding_context(
    mcp_context_result: dict[str, Any] | None,
    *,
    max_lines: int | None = None,
    max_chars: int | None = None,
) -> dict[str, Any]:
    settings = load_settings_safe()
    resolved_max_lines = max_lines if max_lines is not None else getattr(settings, "code_context_max_lines", 200)
    resolved_max_chars = max_chars if max_chars is not None else getattr(settings, "code_context_max_chars", 8000)

    if not mcp_context_result or not mcp_context_result.get("ok"):
        return {
            "available": False,
            "file_path": None,
            "language": None,
            "source": None,
            "excerpt": "",
            "truncated": False,
            "prompt_block": "",
            "notice": "Active code context unavailable.",
            "error": (mcp_context_result or {}).get("error"),
        }

    data = mcp_context_result.get("data") or {}
    file_path = data.get("file") or data.get("path") or None
    language = data.get("language") or data.get("lang") or None

    raw_text, source = _choose_source_text(data)
    if not raw_text:
        return {
            "available": False,
            "file_path": file_path,
            "language": language,
            "source": None,
            "excerpt": "",
            "truncated": False,
            "prompt_block": "",
            "notice": "Active code context unavailable.",
            "error": {"code": "mcp_no_text", "message": "No selection/visible/content text in MCP payload", "recoverable": True},
        }

    excerpt, truncated = bound_text(raw_text, max_lines=resolved_max_lines, max_chars=resolved_max_chars)
    bounded = BoundedCodeContext(
        file_path=str(file_path) if file_path is not None else None,
        language=str(language) if language is not None else None,
        source=source,
        excerpt=excerpt,
        truncated=truncated,
    )

    header_bits: list[str] = []
    if bounded.file_path:
        header_bits.append(f"Active file: {bounded.file_path}")
    if bounded.language:
        header_bits.append(f"Language: {bounded.language}")
    if bounded.source:
        header_bits.append(f"Source: {bounded.source}")
    if bounded.truncated:
        header_bits.append("Note: excerpt truncated for safety.")

    header = "\n".join(header_bits).strip()
    prompt_block = (header + "\n\n" if header else "") + "```" + "\n" + bounded.excerpt + "\n```"

    return {
        "available": True,
        "file_path": bounded.file_path,
        "language": bounded.language,
        "source": bounded.source,
        "excerpt": bounded.excerpt,
        "truncated": bounded.truncated,
        "prompt_block": prompt_block,
        "notice": "",
        "error": None,
    }


def build_codebase_search_block(
    search_results: list[dict[str, Any]] | None = None,
    file_tree: list[str] | None = None,
    related_files: list[dict[str, Any]] | None = None,
) -> str:
    parts: list[str] = []

    if file_tree:
        tree_preview = file_tree[:50]
        parts.append("## Project Structure (first 50 files)")
        parts.append("```")
        parts.extend(tree_preview)
        if len(file_tree) > 50:
            parts.append(f"... and {len(file_tree) - 50} more files")
        parts.append("```")

    if search_results and len(search_results) > 0:
        parts.append("## Codebase Search Results")
        parts.append("The following matches were found across the project:")
        parts.append("")
        for r in search_results[:15]:
            parts.append(f"- `{r['file']}:{r['line']}` — {r['snippet']}")

    if related_files:
        parts.append("## Related Files (imports/references)")
        for rf in related_files[:5]:
            content = rf.get("content", "")
            lines = content.splitlines()[:30]
            preview = "\n".join(lines)
            parts.append(f"### {rf.get('file', 'unknown')}")
            parts.append("```")
            parts.append(preview[:1500])
            parts.append("```")

    return "\n".join(parts)
