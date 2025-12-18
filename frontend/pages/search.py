from fasthtml.common import *
import httpx
from typing import Optional, List, Dict
import sys
import os

# Add parent directory to path to import shared modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.layout import base_layout

API_BASE = "http://localhost:8000"

def search_page_layout(content):
    """Common layout for search pages"""
    return base_layout(
        "Search Documents - Document Control System",
        content
    )

async def get_users_for_select():
    """Fetch all users for dropdown selection"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{API_BASE}/users")
            response.raise_for_status()
            return response.json()
    except Exception as e:
        print(f"Error fetching users: {e}")
        return []

async def search_documents(query: str, user_id: str, top_k: int = 5):
    """
    Search documents using RAG.
    Sends user_id in request body.
    """
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            data = {
                "query": query,
                "user_id": user_id,
                "top_k": top_k
            }
            response = await client.post(
                f"{API_BASE}/search",
                json=data
            )
            response.raise_for_status()
            result = response.json()

            # Debug: Print the response to see what we're getting
            print(f"Search API response: {result}")

            return result, None
    except httpx.HTTPStatusError as e:
        error_detail = e.response.json().get("detail", e.response.text) if e.response.headers.get("content-type") == "application/json" else e.response.text
        return None, f"Error: {error_detail}"
    except httpx.TimeoutException:
        return None, "Request timed out. Please try again with a simpler query."
    except Exception as e:
        return None, f"Error searching documents: {str(e)}"

def render_search_page(users: List[Dict], selected_user_id: Optional[str] = None,
                      search_query: Optional[str] = None, top_k: int = 5,
                      search_results: Optional[Dict] = None, error: Optional[str] = None):
    """Render the search page"""

    return search_page_layout(
        Div(
            Div(
                H1("Search Documents"),
                A("Back to Home", href="/", cls="btn btn-secondary"),
                cls="header"
            ),

            Div(
                error and Div(error, cls="error") or None,

                Div(
                    P(Strong("Search through your documents using RAG"),
                      " - Retrieval Augmented Generation technology finds the most relevant content."),
                    P("Select a user to search as (for permissions), then enter your search query."),
                    cls="info-box"
                ),

                # Search form
                Div(
                    Form(
                        Div(
                            Div(
                                Span("Search as User:", cls="form-label"),
                                Select(
                                    Option("Select a user...", value="", selected=not selected_user_id),
                                    *[Option(
                                        f"{user.get('full_name') or user.get('email')} ({user.get('email')})",
                                        value=user['id'],
                                        selected=(selected_user_id == user['id'])
                                    ) for user in users],
                                    name="user_id",
                                    cls="user-select",
                                    required=True
                                ),
                                cls="form-group"
                            ),
                            Div(
                                Span("Max Results:", cls="form-label"),
                                Input(
                                    type="number",
                                    name="top_k",
                                    value=str(top_k),
                                    min="1",
                                    max="20",
                                    cls="top-k-input",
                                    title="Number of results to return (1-20)"
                                ),
                                cls="form-group"
                            ),
                            cls="form-row"
                        ),

                        Div(
                            Input(
                                type="text",
                                name="query",
                                placeholder="Enter your search query...",
                                cls="search-input",
                                value=search_query or "",
                                required=True,
                                autofocus=True
                            ),
                            Button("Search", type="submit", cls="btn"),
                            cls="search-form"
                        ),

                        method="POST",
                        action="/search"
                    ),
                    cls="search-section"
                ),

                # Results section
                search_results and Div(
                    Div(
                        P(Strong(f"Found {search_results.get('total', 0)} results"),
                          f" for query: \"{search_results.get('query', '')}\""),
                        cls="results-summary"
                    ),

                    search_results.get('results') and len(search_results.get('results', [])) > 0 and Div(
                        *[Div(
                            Div(
                                A(
                                    result.get('title', 'Untitled Document'),
                                    href=f"/documents/{result.get('document_id')}",
                                    cls="result-title"
                                ),
                                Span(
                                    f"Score: {result.get('score', 0):.2f}",
                                    cls=f"result-score {get_score_class(result.get('score', 0))}"
                                ),
                                cls="result-header"
                            ),

                            Div(
                                result.get('content', 'No content preview available'),
                                cls="result-content"
                            ),

                            Div(
                                Div(
                                    Span("Document ID:", cls="result-meta-label"),
                                    Span(result.get('document_id', 'N/A')),
                                    cls="result-meta-item"
                                ),
                                result.get('version_id') and Div(
                                    Span("Version ID:", cls="result-meta-label"),
                                    Span(result.get('version_id')),
                                    cls="result-meta-item"
                                ) or None,
                                cls="result-meta"
                            ),

                            cls="result-item"
                        ) for result in search_results.get('results', [])]
                    ) or Div(
                        H3("No results found"),
                        P("Try adjusting your search query or using different keywords."),
                        cls="no-results"
                    ),

                    cls="results-section"
                ) or (selected_user_id and search_query and Div(
                    H3("No results to display"),
                    P("Your search did not return any results."),
                    cls="empty-state"
                )) or Div(
                    H3("Start searching"),
                    P("Select a user and enter a search query to find relevant documents."),
                    cls="empty-state"
                ),

                cls="content"
            )
        )
    )

def get_score_class(score: float) -> str:
    """Return CSS class based on relevance score"""
    if score >= 0.8:
        return "score-high"
    elif score >= 0.6:
        return "score-medium"
    else:
        return "score-low"
