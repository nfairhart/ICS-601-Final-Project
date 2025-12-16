from fasthtml.common import *
from frontend.lib.api import http_client
from frontend.components.navbar import navbar


def register(rt):
    @rt('/search')
    def get():
        # Preload users for permission-based search
        try:
            users_resp = http_client.get('/users')
            users = users_resp.json() if users_resp.status_code == 200 else []
        except Exception:
            users = []

        return Div(
            navbar('search'),
            Titled('🔍 RAG Document Search',
                
                # Info Card
                Div(
                    H3("About RAG Search"),
                    P("RAG (Retrieval-Augmented Generation) uses AI embeddings to find semantically similar content across your documents."),
                    P(Strong("How it works: "), "Your query is converted to an embedding vector and compared against document embeddings to find the most relevant matches, even if exact keywords don't match."),
                    Details(
                        Summary("💡 Search Tips"),
                        Ul(
                            Li("Use natural language queries like 'documents about marketing strategy'"),
                            Li("Results are ranked by semantic similarity (0.00 - 1.00)"),
                            Li("Higher relevance scores mean better matches"),
                            Li("You can only search documents you have permission to access"),
                        ),
                        style="margin-top: 1rem;"
                    ),
                    cls="card"
                ),
                
                # Search Form
                Div(
                    H3("🔎 Search Documents"),
                    Form(
                        Div(
                            Label('Search Query:', For='query'),
                            Input(
                                type='text',
                                id='query',
                                name='query',
                                required=True,
                                placeholder='e.g., "documents about Q4 sales" or "marketing strategy"',
                                style="width: 100%;"
                            ),
                            cls="form-row"
                        ),
                        Div(
                            Label('Search as User:', For='user_id'),
                            Select(
                                *[Option(
                                    f"{u.get('full_name', 'No Name')} ({u['email']})",
                                    value=u['id']
                                ) for u in users],
                                id='user_id',
                                name='user_id',
                                required=True
                            ) if users else P("⚠️ No users available. Create a user first."),
                            P("Results will be filtered based on this user's document permissions.", 
                              style="font-size: 0.9em; color: #666; margin-top: 0.5rem;"),
                            cls="form-row"
                        ),
                        Div(
                            Label('Number of Results:', For='top_k'),
                            Input(
                                type='number',
                                id='top_k',
                                name='top_k',
                                value='5',
                                min='1',
                                max='20'
                            ),
                            cls="form-row"
                        ),
                        Button('Search 🚀', type='submit') if users else None,
                        hx_post='/search/run',
                        hx_target='#search-results',
                        hx_swap='innerHTML',
                        hx_indicator='#search-loading'
                    ),
                    cls="card"
                ),
                
                # Loading Indicator
                Div(
                    P("🔄 Searching...", style="color: #0066cc; font-weight: 600;"),
                    id="search-loading",
                    cls="htmx-indicator card"
                ),
                
                # Results Container
                Div(
                    P("👆 Enter a query above to search your documents", style="color: #666; text-align: center;"),
                    id='search-results'
                )
            )
        )

    @rt('/search/run')
    async def post(query: str, user_id: str, top_k: int = 5):
        try:
            resp = http_client.post('/search', json={
                'query': query,
                'user_id': user_id,
                'top_k': top_k
            })
            
            if resp.status_code != 200:
                return Div(
                    P('❌ Search failed', style='color: #dc3545; font-weight: 600;'),
                    P(f"Error: {resp.json().get('detail', 'Unknown error')}", style='color: #666;'),
                    cls="card"
                )
            
            data = resp.json()
            results = data.get('results', [])
            total = data.get('total', 0)
            
            if not results:
                return Div(
                    H3("No Results Found"),
                    P(f"No documents matched your query: '{query}'"),
                    P("Try:"),
                    Ul(
                        Li("Using different keywords"),
                        Li("Making your query more general"),
                        Li("Checking if you have access to relevant documents"),
                    ),
                    cls="card"
                )
            
            return Div(
                Div(
                    H3(f"✅ Found {total} Result{'s' if total != 1 else ''}"),
                    P(f"Query: '{query}'", style="color: #666;"),
                    cls="card"
                ),
                *[search_result_card(r, i+1) for i, r in enumerate(results)]
            )
            
        except Exception as e:
            return Div(
                P(f'❌ Error: {str(e)}', style='color: #dc3545; font-weight: 600;'),
                cls="card"
            )


def search_result_card(r: dict, rank: int):
    score = r.get('relevance_score') or r.get('relevance') or 0
    title = r.get('title') or 'Untitled'
    content = r.get('content') or ''
    doc_id = r.get('document_id')
    
    # Color code relevance score
    if score >= 0.8:
        score_color = '#28a745'  # Green - Excellent match
        match_quality = 'Excellent Match'
    elif score >= 0.6:
        score_color = '#0066cc'  # Blue - Good match
        match_quality = 'Good Match'
    elif score >= 0.4:
        score_color = '#ffc107'  # Yellow - Fair match
        match_quality = 'Fair Match'
    else:
        score_color = '#6c757d'  # Gray - Weak match
        match_quality = 'Weak Match'
    
    return Div(
        Div(
            Span(f"#{rank}", style="font-size: 1.2em; font-weight: 700; color: #666; margin-right: 0.5rem;"),
            H4(title, style="display: inline; margin: 0;"),
            style="margin-bottom: 0.5rem;"
        ),
        P(
            Strong('Relevance: '),
            Span(f"{score:.3f}", style=f"color: {score_color}; font-weight: 700;"),
            Span(f" • {match_quality}", style=f"color: {score_color}; font-weight: 600; margin-left: 0.5rem;"),
            style="margin: 0.5rem 0;"
        ),
        P(
            Strong('Document ID: '),
            Code(doc_id),
            style="margin: 0.5rem 0; font-size: 0.9em;"
        ),
        Div(
            P(Strong("Content Preview:")),
            P(
                content[:400] + ('...' if len(content) > 400 else ''),
                style="background: #f8f9fa; padding: 1rem; border-left: 3px solid #0066cc; margin: 0.5rem 0; white-space: pre-wrap;"
            ),
        ),
        Div(
            Button(
                '📄 View Full Document',
                onclick=f"window.location='/documents/{doc_id}'",
                style="background: #0066cc;"
            ),
            Button(
                '🤖 Ask AI About This',
                onclick=f"window.location='/chat?doc={doc_id}'",
                style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none;"
            ),
            cls="btn-group"
        ),
        cls="card",
        style=f"border-left: 4px solid {score_color};"
    )