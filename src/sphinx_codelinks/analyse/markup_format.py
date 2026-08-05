"""Convert source-comment content between markup formats.

The markup language used inside source-code comments depends on the
programming language: some ecosystems conventionally write documentation
comments in Markdown (e.g. Rust doc comments, Go doc comments), while
Sphinx-Needs renders a need's title and body as reStructuredText (RST). When
Markdown-authored text is fed verbatim into a need, its markup would be
interpreted as RST and render incorrectly.

This module converts captured comment content (a one-line marker's title and
description) into RST *only* for languages that are statically configured to
use a non-RST comment markup. The mapping is intentionally static (not
user-configurable) and conservative: languages default to ``plain`` (no
conversion, preserving existing behaviour) unless explicitly listed in
:data:`LANGUAGE_MARKUP_FORMATS`.

The design is extensible: adding support for another markup format is a
matter of adding a member to :class:`MarkupFormat` and a converter in
:data:`_CONVERTERS`.
"""

from collections.abc import Callable
from enum import Enum

from sphinx_codelinks.logger import get_logger
from sphinx_codelinks.source_discover.config import CommentType

logger = get_logger(__name__)


class MarkupFormat(str, Enum):
    """Markup format a language uses inside its source-code comments.

    ``plain`` is treated as already-RST (or plain text) and passed through
    unchanged. Any other member is converted to RST before the content is
    handed to Sphinx-Needs.
    """

    plain = "plain"
    markdown = "markdown"


#: Static mapping of source language to the markup format used in its
#: comments. Languages absent from this mapping default to
#: :attr:`MarkupFormat.plain` (no conversion). This is the sole enablement
#: switch for comment markup conversion.
#:
#: Only languages whose comment conventions are predominantly Markdown are
#: listed here. Add or remove entries to change which languages get their
#: one-line marker content (title and description) converted.
LANGUAGE_MARKUP_FORMATS: dict[CommentType, MarkupFormat] = {
    CommentType.rust: MarkupFormat.markdown,
    CommentType.go: MarkupFormat.markdown,
}


def format_for_language(comment_type: CommentType) -> MarkupFormat:
    """Return the configured comment markup format for a language.

    :param comment_type: The language whose comments are being analysed.
    :return: The statically configured format, or :attr:`MarkupFormat.plain`
        if the language is not listed.
    """
    return LANGUAGE_MARKUP_FORMATS.get(comment_type, MarkupFormat.plain)


def _convert_markdown(text: str) -> str:
    """Convert Markdown text to reStructuredText using ``m2r2``.

    ``m2r2`` is an optional dependency; if it is not installed the original
    text is returned unchanged and a warning is emitted so the build still
    succeeds (the content simply renders as-is).

    :param text: Markdown-formatted text.
    :return: The equivalent reStructuredText, or ``text`` unchanged when
        ``m2r2`` is unavailable.
    """
    try:
        from m2r2 import convert as _md_to_rst
    except ImportError:
        logger.warning(
            "Markdown comment conversion requires the 'm2r2' package. "
            "Install it (e.g. `pip install sphinx-codelinks[markdown]`) to "
            "enable Markdown->RST conversion; the content will be used "
            "verbatim for now.",
            subtype="missing_markdown_dependency",
        )
        return text
    # m2r2 appends a trailing newline; strip it so content stays tight.
    rst: str = _md_to_rst(text)
    return rst.strip()


#: Registry of format-specific converters. ``plain`` has no entry and is a
#: no-op. Extend this to support additional formats.
_CONVERTERS: dict[MarkupFormat, Callable[[str], str]] = {
    MarkupFormat.markdown: _convert_markdown,
}


def convert_markup(text: str, fmt: MarkupFormat) -> str:
    """Convert comment content from ``fmt`` to reStructuredText.

    :param text: The captured comment content.
    :param fmt: The markup format ``text`` is authored in.
    :return: The content as reStructuredText. For :attr:`MarkupFormat.plain`
        (or an empty ``text``) the input is returned unchanged.
    """
    if not text:
        return text
    converter = _CONVERTERS.get(fmt)
    if converter is None:
        return text
    return converter(text)
