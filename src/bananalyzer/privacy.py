PERSISTENCE_ALLOWED_CATEGORIES = [
    "Goals",
    "Session summaries",
    "Recurring coding mistakes",
    "Progress",
    "Banana debt",
    "State transitions",
    "Integration health",
    "User-approved memory notes",
    "Minimal diagnostic metadata"
]

DEFAULT_MAX_PERSISTED_STRING_LENGTH = 800
DEFAULT_MAX_PERSISTED_LIST_ITEMS = 50
DEFAULT_MAX_PERSISTED_NESTING = 6

_LARGE_TEXT_KEYS = {
    "code",
    "content",
    "selection",
    "visible",
    "text",
    "raw",
    "prompt",
    "messages",
}


def is_category_allowed(category: str) -> bool:
    return category in PERSISTENCE_ALLOWED_CATEGORIES


def is_content_safe_for_persistence(
    content,
    *,
    max_length: int = DEFAULT_MAX_PERSISTED_STRING_LENGTH,
) -> bool:
    if content is None:
        return False

    if isinstance(content, str):
        return len(content) <= max_length

    if isinstance(content, dict):
        for key, value in content.items():
            key_str = str(key).lower()
            if key_str in _LARGE_TEXT_KEYS and isinstance(value, str) and len(value) > 200:
                return False
        return True

    return True


def check_before_persistence(category: str, content) -> tuple[bool, str | None]:
    if not is_category_allowed(category):
        return False, f"Category '{category}' is not in the persistence allowlist"

    if not is_content_safe_for_persistence(content):
        if isinstance(content, str) and len(content) > DEFAULT_MAX_PERSISTED_STRING_LENGTH:
            return False, f"Content too large for persistence ({len(content)} chars, max {DEFAULT_MAX_PERSISTED_STRING_LENGTH})"
        if isinstance(content, dict):
            for key, value in content.items():
                key_str = str(key).lower()
                if key_str in _LARGE_TEXT_KEYS and isinstance(value, str) and len(value) > 200:
                    return False, f"Content contains large text in key '{key}' which requires summarization"
        return False, "Content failed safety checks for persistence"

    return True, None


def sanitize_for_persistence(
    value,
    *,
    max_string_length: int = DEFAULT_MAX_PERSISTED_STRING_LENGTH,
    max_list_items: int = DEFAULT_MAX_PERSISTED_LIST_ITEMS,
    max_nesting: int = DEFAULT_MAX_PERSISTED_NESTING,
    _depth: int = 0,
):
    if _depth >= max_nesting:
        return "<truncated>"

    if value is None:
        return None

    if isinstance(value, str):
        if len(value) <= max_string_length:
            return value
        return value[:max_string_length] + "...(truncated)"

    if isinstance(value, (int, float, bool)):
        return value

    if isinstance(value, dict):
        sanitized = {}
        for key, v in value.items():
            key_str = str(key)
            if key_str.lower() in _LARGE_TEXT_KEYS and isinstance(v, str) and len(v) > 200:
                sanitized[key_str] = "<redacted>"
                continue
            sanitized[key_str] = sanitize_for_persistence(
                v,
                max_string_length=max_string_length,
                max_list_items=max_list_items,
                max_nesting=max_nesting,
                _depth=_depth + 1,
            )
        return sanitized

    if isinstance(value, (list, tuple)):
        limited = list(value)[:max_list_items]
        return [
            sanitize_for_persistence(
                item,
                max_string_length=max_string_length,
                max_list_items=max_list_items,
                max_nesting=max_nesting,
                _depth=_depth + 1,
            )
            for item in limited
        ]

    try:
        return str(value)
    except Exception:
        return "<unserializable>"
