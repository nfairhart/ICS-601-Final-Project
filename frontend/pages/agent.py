from fasthtml.common import *
import httpx
from typing import Optional, List, Dict

API_BASE = "http://localhost:8000"

def agent_page_layout(content):
    """Common layout for AI agent pages"""
    return Html(
        Head(
            Title("AI Agent - Document Control System"),
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
                .chat-container {
                    display: flex;
                    flex-direction: column;
                    height: 600px;
                }
                .chat-history {
                    flex-grow: 1;
                    overflow-y: auto;
                    padding: 20px;
                    background: #f8f9fa;
                    border-radius: 8px;
                    margin-bottom: 20px;
                }
                .message {
                    margin-bottom: 20px;
                    padding: 15px;
                    border-radius: 8px;
                }
                .message.user {
                    background: #007bff;
                    color: white;
                    margin-left: 20%;
                    text-align: right;
                }
                .message.agent {
                    background: white;
                    color: #333;
                    margin-right: 20%;
                    border: 1px solid #dee2e6;
                }
                .message-label {
                    font-weight: bold;
                    margin-bottom: 8px;
                    font-size: 12px;
                    text-transform: uppercase;
                }
                .message.user .message-label {
                    color: #cce5ff;
                }
                .message.agent .message-label {
                    color: #6c757d;
                }
                .message-text {
                    line-height: 1.6;
                    white-space: pre-wrap;
                    word-wrap: break-word;
                }
                .query-form {
                    display: flex;
                    gap: 10px;
                    align-items: flex-start;
                }
                .query-input {
                    flex-grow: 1;
                    padding: 12px;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    font-size: 14px;
                    font-family: inherit;
                    resize: vertical;
                    min-height: 60px;
                }
                .query-input:focus {
                    outline: none;
                    border-color: #007bff;
                }
                .user-select {
                    padding: 12px;
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
                .form-row {
                    display: flex;
                    gap: 10px;
                    margin-bottom: 15px;
                    align-items: center;
                }
                .form-label {
                    font-weight: bold;
                    color: #333;
                    min-width: 100px;
                }
                .error {
                    color: #dc3545;
                    padding: 10px;
                    background: #f8d7da;
                    border-radius: 4px;
                    margin-bottom: 20px;
                }
                .loading {
                    text-align: center;
                    padding: 20px;
                    color: #6c757d;
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
                .empty-state p {
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
                .example-queries {
                    margin-top: 20px;
                }
                .example-queries h4 {
                    color: #333;
                    margin-bottom: 10px;
                }
                .example-query {
                    padding: 10px;
                    background: #f8f9fa;
                    border-radius: 4px;
                    margin-bottom: 8px;
                    cursor: pointer;
                    border: 1px solid #dee2e6;
                }
                .example-query:hover {
                    background: #e9ecef;
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

async def query_agent(query: str, user_id: str):
    """Query the AI agent"""
    try:
        async with httpx.AsyncClient(timeout=180.0) as client:
            data = {
                "query": query,
                "user_id": user_id
            }
            response = await client.post(f"{API_BASE}/agent/query", json=data)
            response.raise_for_status()
            return response.json(), None
    except httpx.HTTPStatusError as e:
        return None, f"Error: {e.response.text}"
    except httpx.TimeoutException:
        return None, "Request timed out. The agent might be processing a complex query."
    except Exception as e:
        return None, f"Error querying agent: {str(e)}"

def render_agent_page(users: List[Dict], selected_user_id: Optional[str] = None,
                     chat_history: Optional[List[Dict]] = None, error: Optional[str] = None):
    """Render the AI agent query page"""

    # Example queries to show users
    example_queries = [
        "Summarize all project proposals from 2024",
        "What are the key deliverables mentioned in the documents?",
        "List all documents related to security",
        "What is the status of the Q1 project?",
        "Show me all archived documents"
    ]

    return agent_page_layout(
        Div(
            Div(
                H1("AI Agent"),
                A("Back to Home", href="/", cls="btn btn-secondary"),
                cls="header"
            ),

            Div(
                error and Div(error, cls="error") or None,

                Div(
                    P(Strong("Ask questions about your documents"),
                      " - The AI agent will search and analyze documents you have access to."),
                    P("Select a user to query as, then type your question below."),
                    cls="info-box"
                ),

                # User selection form
                Form(
                    Div(
                        Span("Query as User:", cls="form-label"),
                        Select(
                            Option("Select a user...", value="", selected=not selected_user_id),
                            *[Option(
                                f"{user.get('full_name') or user.get('email')} ({user.get('email')})",
                                value=user['id'],
                                selected=(selected_user_id == user['id'])
                            ) for user in users],
                            name="user_id",
                            cls="user-select",
                            required=True,
                            onchange="this.form.submit()"
                        ),
                        cls="form-row"
                    ),
                    method="GET",
                    action="/agent"
                ),

                Hr(),

                # Chat interface
                selected_user_id and Div(
                    # Chat history
                    Div(
                        chat_history and len(chat_history) > 0 and Div(
                            *[Div(
                                Div(msg.get("role", "").upper(), cls="message-label"),
                                Div(msg.get("content", ""), cls="message-text"),
                                cls=f"message {msg.get('role', 'agent')}"
                            ) for msg in chat_history]
                        ) or Div(
                            H3("Start a conversation"),
                            P("Ask the AI agent anything about your documents."),
                            cls="empty-state"
                        ),
                        cls="chat-history",
                        id="chat-history"
                    ),

                    # Query form
                    Form(
                        Div(
                            Textarea(
                                name="query",
                                placeholder="Ask a question about your documents...",
                                cls="query-input",
                                required=True,
                                autofocus=True
                            ),
                            Button("Send Query", type="submit", cls="btn"),
                            cls="query-form"
                        ),
                        Input(type="hidden", name="user_id", value=selected_user_id),
                        method="POST",
                        action="/agent/query"
                    ),

                    cls="chat-container"
                ) or Div(
                    P("Please select a user to start querying the AI agent."),
                    cls="empty-state"
                ),

                # Example queries
                not chat_history and Div(
                    H4("Example Questions:"),
                    *[Div(
                        query,
                        cls="example-query",
                        onclick=f"document.querySelector('.query-input').value = '{query}'"
                    ) for query in example_queries],
                    cls="example-queries"
                ) or None,

                cls="content"
            )
        )
    )

def render_agent_response(users: List[Dict], user_id: str,
                         chat_history: List[Dict], error: Optional[str] = None):
    """Render the page after receiving an agent response"""
    return render_agent_page(
        users=users,
        selected_user_id=user_id,
        chat_history=chat_history,
        error=error
    )
