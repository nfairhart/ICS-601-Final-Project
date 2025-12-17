"""Shared layout components for the frontend"""
from fasthtml.common import Html, Head, Title, Style, Body
from .styles import COMMON_STYLES


def base_layout(title: str, content, additional_styles: str = ""):
    """
    Base layout for all pages.

    Args:
        title: Page title
        content: Page content (fasthtml components)
        additional_styles: Optional additional CSS styles specific to the page
    """
    return Html(
        Head(
            Title(title),
            Style(COMMON_STYLES + additional_styles)
        ),
        Body(content)
    )
