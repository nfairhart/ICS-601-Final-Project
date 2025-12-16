from fasthtml.common import *
from frontend.lib.api import http_client, API_BASE_URL
from frontend.components.navbar import navbar


def register(rt):
    @rt('/')
    def get():
        # Fetch stats from API
        try:
            docs_resp = http_client.get('/documents')
            documents = docs_resp.json() if docs_resp.status_code == 200 else []
            
            users_resp = http_client.get('/users')
            users = users_resp.json() if users_resp.status_code == 200 else []
            
            # Calculate stats
            total_docs = len(documents)
            active_docs = len([d for d in documents if d.get('status') == 'Active'])
            draft_docs = len([d for d in documents if d.get('status') == 'Draft'])
            archived_docs = len([d for d in documents if d.get('status') == 'Archived'])
            total_users = len(users)
            
        except Exception:
            total_docs = 0
            active_docs = 0
            draft_docs = 0
            archived_docs = 0
            total_users = 0
        
        return Div(
            navbar("home"),
            Titled(
                "📊 Document Management Dashboard",
                
                # Stats Overview
                Div(
                    H3("System Overview"),
                    Div(
                        # Documents Stats
                        Div(
                            Div(
                                H2(str(total_docs), style="margin: 0; color: #0066cc;"),
                                P("Total Documents", style="margin: 0.5rem 0 0 0; color: #666;")
                            ),
                            cls="stat-card"
                        ),
                        Div(
                            Div(
                                H2(str(active_docs), style="margin: 0; color: #28a745;"),
                                P("Active", style="margin: 0.5rem 0 0 0; color: #666;")
                            ),
                            cls="stat-card"
                        ),
                        Div(
                            Div(
                                H2(str(draft_docs), style="margin: 0; color: #ffc107;"),
                                P("Drafts", style="margin: 0.5rem 0 0 0; color: #666;")
                            ),
                            cls="stat-card"
                        ),
                        Div(
                            Div(
                                H2(str(archived_docs), style="margin: 0; color: #6c757d;"),
                                P("Archived", style="margin: 0.5rem 0 0 0; color: #666;")
                            ),
                            cls="stat-card"
                        ),
                        Div(
                            Div(
                                H2(str(total_users), style="margin: 0; color: #9c27b0;"),
                                P("Total Users", style="margin: 0.5rem 0 0 0; color: #666;")
                            ),
                            cls="stat-card"
                        ),
                        cls="stats-grid"
                    ),
                    cls="card"
                ),
                
                # Quick Actions
                Div(
                    H3("Quick Actions"),
                    Div(
                        Button(
                            "👤 Manage Users",
                            onclick="window.location='/users'",
                            style="flex: 1;"
                        ),
                        Button(
                            "📄 Manage Documents", 
                            onclick="window.location='/documents'",
                            style="flex: 1;"
                        ),
                        Button(
                            "🔍 Search Documents",
                            onclick="window.location='/search'",
                            style="flex: 1;"
                        ),
                        Button(
                            "🤖 AI Assistant",
                            onclick="window.location='/chat'",
                            style="flex: 1; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none;"
                        ),
                        cls="btn-group"
                    ),
                    cls="card"
                ),
                
                # Features Overview
                Div(
                    H3("System Features"),
                    Ul(
                        Li(Strong("User Management:"), " Create, update, and manage user accounts with role-based access"),
                        Li(Strong("Document Management:"), " Upload, version, and organize documents with status tracking"),
                        Li(Strong("Permissions:"), " Fine-grained access control for documents per user"),
                        Li(Strong("RAG Search:"), " Semantic search across all your documents using AI embeddings"),
                        Li(Strong("AI Assistant:"), " Chat with an intelligent agent that can search, summarize, and analyze your documents"),
                        Li(Strong("Version Control:"), " Track document changes with full version history"),
                    ),
                    cls="card"
                ),
                
                # API Documentation Link
                Div(
                    H3("Developer Resources"),
                    P("Access the full API documentation for integration and development:"),
                    A(
                        "📚 View API Documentation →",
                        href=f"{API_BASE_URL}/docs",
                        target="_blank",
                        style="display: inline-block; padding: 0.75rem 1.5rem; background: #0066cc; color: white; text-decoration: none; border-radius: 6px; font-weight: 600;"
                    ),
                    cls="card"
                )
            )
        )