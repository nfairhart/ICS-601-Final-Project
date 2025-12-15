from fasthtml.common import *


def navbar(active: str = "home"):
    def link(label, href, key):
        style = "font-weight: 700;" if active == key else ""
        return Li(A(label, href=href), style=style)

    return Nav(
        Ul(
            link("Home", "/", "home"),
            link("Users", "/users", "users"),
            link("Documents", "/documents", "documents"),
            link("Search", "/search", "search"),
            style="display: flex; gap: 1rem; list-style: none; padding: 0;"
        ),
        Hr()
    )
