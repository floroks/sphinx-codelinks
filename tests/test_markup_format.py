"""Unit tests for comment markup format conversion.

Covers the static language enablement map and the Markdown->RST conversion
used for one-line marker content, i.e. title and description (see
``sphinx_codelinks.analyse.markup_format``).
"""

import pytest

from sphinx_codelinks.analyse import markup_format as mf
from sphinx_codelinks.analyse.markup_format import (
    MarkupFormat,
    convert_markup,
    format_for_language,
)
from sphinx_codelinks.source_discover.config import CommentType


@pytest.mark.parametrize(
    ("comment_type", "expected"),
    [
        (CommentType.rust, MarkupFormat.markdown),
        (CommentType.go, MarkupFormat.markdown),
        (CommentType.cpp, MarkupFormat.plain),
        (CommentType.python, MarkupFormat.plain),
        (CommentType.cs, MarkupFormat.plain),
        (CommentType.yaml, MarkupFormat.plain),
        (CommentType.jsonc, MarkupFormat.plain),
    ],
)
def test_format_for_language(comment_type: CommentType, expected: MarkupFormat):
    """Only statically-enabled languages resolve to a non-plain format."""
    assert format_for_language(comment_type) == expected


def test_convert_plain_is_noop():
    """Plain format returns the text unchanged."""
    text = "Calls `do_thing()` and returns **fast**."
    assert convert_markup(text, MarkupFormat.plain) == text


def test_convert_empty_is_noop():
    """Empty text is returned unchanged regardless of format."""
    assert convert_markup("", MarkupFormat.markdown) == ""


def test_convert_markdown_inline():
    """Markdown inline markup is converted to RST equivalents."""
    result = convert_markup(
        "Calls `do_thing()` and returns **fast**.",
        MarkupFormat.markdown,
    )
    assert "``do_thing()``" in result
    assert "**fast**" in result
    # No leading/trailing whitespace remains.
    assert result == result.strip()


def test_convert_markdown_title_inline():
    """A single-line title converts inline markup without block wrapping."""
    result = convert_markup("Calls `do_thing()` fast", MarkupFormat.markdown)
    assert result == "Calls ``do_thing()`` fast"


def test_convert_markdown_list():
    """Markdown bullet lists become RST bullet lists."""
    result = convert_markup("- a\n- b", MarkupFormat.markdown)
    assert "* a" in result
    assert "* b" in result


def test_convert_markdown_missing_dependency(monkeypatch, capsys):
    """When m2r2 is unavailable, text is returned verbatim with a warning."""
    import builtins

    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "m2r2":
            raise ImportError("No module named 'm2r2'")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)

    text = "Calls `do_thing()`."
    assert mf._convert_markdown(text) == text  # noqa: SLF001
