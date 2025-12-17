from fasthtml.common import *
import httpx
from typing import Optional, List, Dict

API_BASE = "http://localhost:8000"

def search_page_layout(content):
    """Common layout for search pages"""
    return Html(
        Head(
            Title("Search Documents - Document Control System"),
            Style("""
                body {
                    font-family: Arial, sans-serif;
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 20px;
                    background: #f5f5f5;
                }
                .header {
                    background: white;
                    padding: 20px;
                    border-radius: 8px;
                    margin-bottom: 20px;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                }
                .btn {
                    display: inline-block;
                    padding: 10px 20px;
                    background: #007bff;
                    color: white;
                    text-decoration: none;
                    border-radius: 4px;
                    border: none;
                    cursor: pointer;
                    font-size: 14px;
                }
                .btn:hover {
                    background: #0056b3;
                }
                .btn-secondary {
                    background: #6c757d;
                }
                .btn-secondary:hover {
                    background: #545b62;
                }
                .content {
                    background: white;
                    padding: 30px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }
                .search-section {
                    margin-bottom: 30px;
                }
                .search-form {
                    display: flex;
                    gap: 10px;
                    margin-bottom: 20px;
                }
                .search-input {
                    flex-grow: 1;
                    padding: 12px;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    font-size: 14px;
                }
                .search-input:focus {
                    outline: none;
                    border-color: #007bff;
                }
                .form-row {
                    display: flex;
                    gap: 15px;
                    margin-bottom: 15px;
                    align-items: center;
                    flex-wrap: wrap;
                }
                .form-group {
                    display: flex;
                    align-items: center;
                    gap: 10px;
                }
                .form-label {
                    font-weight: bold;
                    color: #333;
                    white-space: nowrap;
                }
                .user-select {
                    padding: 10px;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    font-size: 14px;
                    background: white;
                    cursor: pointer;
                    min-width: 250px;
                }
                .user-select:focus {
                    outline: none;
                    border-color: #007bff;
                }
                .top-k-input {
                    width: 80px;
                    padding: 10px;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    font-size: 14px;
                }
                .top-k-input:focus {
                    outline: none;
                    border-color: #007bff;
                }
                .results-section {
                    margin-top: 30px;
                }
                .result-item {
                    padding: 20px;
                    border: 1px solid #e9ecef;
                    border-radius: 8px;
                    margin-bottom: 15px;
                    background: #f8f9fa;
                }
                .result-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: start;
                    margin-bottom: 10px;
                }
                .result-title {
                    font-size: 18px;
                    font-weight: bold;
                    color: #007bff;
                    margin: 0;
                    text-decoration: none;
                }
                .result-title:hover {
                    text-decoration: underline;
                }
                .result-score {
                    color: white;
                    padding: 4px 12px;
                    border-radius: 12px;
                    font-size: 12px;
                    font-weight: bold;
                }
                .score-high {
                    background: #28a745;
                }
                .score-medium {
                    background: #ffc107;
                    color: #333;
                }
                .score-low {
                    background: #dc3545;
                }
                .result-content {
                    color: #333;
                    line-height: 1.6;
                    margin: 10px 0;
                    padding: 10px;
                    background: white;
                    border-left: 3px solid #007bff;
                    border-radius: 4px;
                }
                .result-meta {
                    display: flex;
                    gap: 20px;
                    color: #6c757d;
                    font-size: 13px;
                    margin-top: 10px;
                }
                .result-meta-item {
                    display: flex;
                    align-items: center;
                    gap: 5px;
                }
                .result-meta-label {
                    font-weight: bold;
                }
                .results-summary {
                    padding: 15px;
                    background: #e7f3ff;
                    border-radius: 4px;
                    margin-bottom: 20px;
                    color: #004085;
                }
                .empty-state {
                    text-align: center;
                    padding: 60px 20px;
                    color: #6c757d;
                }
                .empty-state h3 {
                    margin-top: 0;
                    color: #495057;
                }
                .error {
                    color: #dc3545;
                    padding: 10px;
                    background: #f8d7da;
                    border-radius: 4px;
                    margin-bottom: 20px;
                }
                .info-box {
                    background: #e7f3ff;
                    border-left: 4px solid #007bff;
                    padding: 15px;
                    margin-bottom: 20px;
                    border-radius: 4px;
                }
                .info-box p {
                    margin: 5px 0;
                    color: #004085;
                }
                .no-results {
                    text-align: center;
                    padding: 40px 20px;
                    color: #6c757d;
                    background: #f8f9fa;
                    border-radius: 8px;
                }
            """)
        ),
        Body(content)
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
    """Search documents using RAG"""
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            data = {
                "query": query,
                "user_id": user_id,
                "top_k": top_k
            }
            response = await client.post(f"{API_BASE}/search", json=data)
            response.raise_for_status()
            result = response.json()

            # Debug: Print the response to see what we're getting
            print(f"Search API response: {result}")

            return result, None
    except httpx.HTTPStatusError as e:
        return None, f"Error: {e.response.text}"
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
