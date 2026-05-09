from bananalyzer.context.context_builder import build_bounded_coding_context


def test_build_bounded_coding_context_prefers_selection():
    result = build_bounded_coding_context(
        {
            "ok": True,
            "data": {
                "file": "src/main.py",
                "selection": {"text": "selected()"},
                "visible": {"text": "visible()"},
            },
            "error": None,
        },
        max_lines=200,
        max_chars=8000,
    )

    assert result["available"] is True
    assert result["source"] == "selection"
    assert "selected()" in result["prompt_block"]
    assert "visible()" not in result["prompt_block"]


def test_build_bounded_coding_context_truncates_by_lines():
    long_text = "\n".join([f"line{i}" for i in range(50)])
    result = build_bounded_coding_context(
        {"ok": True, "data": {"selection": long_text}, "error": None},
        max_lines=5,
        max_chars=10000,
    )

    assert result["available"] is True
    assert result["truncated"] is True
    assert len(result["excerpt"].splitlines()) == 5


def test_build_bounded_coding_context_unavailable_when_mcp_fails():
    result = build_bounded_coding_context({"ok": False, "data": None, "error": {"code": "mcp_down"}}, max_lines=200, max_chars=8000)
    assert result["available"] is False
    assert result["notice"]
