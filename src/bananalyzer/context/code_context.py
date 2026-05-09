from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BoundedCodeContext:
    file_path: str | None
    language: str | None
    source: str | None
    excerpt: str
    truncated: bool


def bound_text(text: str, *, max_lines: int, max_chars: int) -> tuple[str, bool]:
    if not text:
        return "", False

    truncated = False

    if max_lines > 0:
        lines = text.splitlines(keepends=True)
        if len(lines) > max_lines:
            lines = lines[:max_lines]
            truncated = True
        text = "".join(lines)

    if max_chars > 0 and len(text) > max_chars:
        text = text[:max_chars]
        truncated = True

    return text, truncated
