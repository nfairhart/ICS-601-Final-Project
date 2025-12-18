"""Shared layout components for the frontend"""
from fasthtml.common import Html, Head, Title, Body


def base_layout(title: str, content):
    """
    Base layout for all pages.

    Args:
        title: Page title
        content: Page content
    """
    return Html(
        Head(
            Title(title)
        ),
        Body(content)
    )
