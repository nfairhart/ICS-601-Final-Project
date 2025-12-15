from fasthtml.common import *
from frontend.lib.api import API_BASE_URL
from frontend.components.navbar import navbar


def register(rt):
    @rt('/')
    def get():
        return Div(
            navbar("home"),
            Titled(
                "Document Management System",
                Card(
                    H2("Welcome to Document Management"),
                    P("Manage your documents, users, and permissions"),
                    Ul(
                        Li(A("Manage Users", href="/users")),
                        Li(A("Manage Documents", href="/documents")),
                        Li(A("Search Documents", href="/search")),
                        Li(A("API Documentation", href=f"{API_BASE_URL}/docs", target="_blank"))
                    )
                )
            )
        )
