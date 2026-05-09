import pytest

from bananalyzer.privacy import (
    PERSISTENCE_ALLOWED_CATEGORIES,
    is_category_allowed,
    is_content_safe_for_persistence,
    check_before_persistence,
    _LARGE_TEXT_KEYS,
    DEFAULT_MAX_PERSISTED_STRING_LENGTH,
)


class TestCategoryAllowlist:
    def test_allowed_categories_pass(self):
        for category in PERSISTENCE_ALLOWED_CATEGORIES:
            assert is_category_allowed(category) is True

    def test_unknown_category_rejected(self):
        assert is_category_allowed("Raw screen captures") is False
        assert is_category_allowed("Code excerpts") is False
        assert is_category_allowed("Audio transcripts") is False

    def test_case_sensitive_match(self):
        assert is_category_allowed("Goals") is True
        assert is_category_allowed("goals") is False

    def test_fuzzy_match_rejected(self):
        assert is_category_allowed("Goals ") is False
        assert is_category_allowed(" Session summaries") is False


class TestContentSafety:
    def test_short_text_allowed(self):
        assert is_content_safe_for_persistence("A short goal description") is True

    def test_text_at_boundary_allowed(self):
        text = "x" * DEFAULT_MAX_PERSISTED_STRING_LENGTH
        assert is_content_safe_for_persistence(text) is True

    def test_text_over_max_length_rejected(self):
        text = "x" * (DEFAULT_MAX_PERSISTED_STRING_LENGTH + 1)
        assert is_content_safe_for_persistence(text) is False

    def test_custom_max_length(self):
        text = "hello world"
        assert is_content_safe_for_persistence(text, max_length=5) is False
        assert is_content_safe_for_persistence(text, max_length=20) is True

    def test_block_large_text_keys_in_dict(self):
        data = {"code": "x" * 201, "goal": "Learn Python"}
        assert is_content_safe_for_persistence(data) is False

    def test_small_text_keys_in_dict_allowed(self):
        data = {"code": "def foo(): pass", "goal": "Learn Rust"}
        assert is_content_safe_for_persistence(data) is True


class TestCheckBeforePersistence:
    def test_allowed_category_and_content_passes(self):
        allowed, reason = check_before_persistence("Goals", "Learn Python")
        assert allowed is True
        assert reason is None

    def test_blocked_category_fails(self):
        allowed, reason = check_before_persistence("Raw code excerpts", "some code")
        assert allowed is False
        assert reason is not None
        assert "category" in reason.lower()

    def test_blocked_content_fails(self):
        allowed, reason = check_before_persistence("Goals", "x" * 1000)
        assert allowed is False
        assert reason is not None
        assert "too large" in reason.lower()

    def test_reason_does_not_contain_blocked_content(self):
        long_text = "SECRET_API_KEY_abc123" * 100
        allowed, reason = check_before_persistence("Goals", long_text)
        assert allowed is False
        assert reason is not None
        assert "SECRET_API_KEY" not in reason
        assert len(reason) < 500

    def test_blocked_large_text_key_content_safe_reason(self):
        data = {"code": "x" * 500, "title": "test"}
        allowed, reason = check_before_persistence("Recurring coding mistakes", data)
        assert allowed is False
        assert reason is not None
        assert "x" * 500 not in reason
        assert len(reason) < 500

    def test_none_content_blocked(self):
        allowed, reason = check_before_persistence("Goals", None)
        assert allowed is False

    def test_session_summaries_allowed_with_short_content(self):
        allowed, reason = check_before_persistence("Session summaries", "Worked on auth module")
        assert allowed is True

    def test_banana_debt_category_allowed(self):
        allowed, reason = check_before_persistence("Banana debt", {"minutes": 30})
        assert allowed is True
