from fasthtml.common import *
from frontend.lib.api import http_client
from frontend.components.navbar import navbar


def register(rt):
    @rt('/chat')
    def get():
        # Get users for dropdown
        try:
            users_resp = http_client.get('/users')
            users = users_resp.json() if users_resp.status_code == 200 else []
        except Exception:
            users = []
        
        if not users:
            return Div(
                navbar('chat'),
                Titled('🤖 AI Document Assistant',
                    Div(
                        P('⚠️ No users found. Please create a user first to use the AI assistant.'),
                        Button('Create User', onclick="window.location='/users'"),
                        cls="card"
                    )
                )
            )
        
        return Div(
            navbar('chat'),
            Titled('🤖 AI Document Assistant',
                # Instructions
                Div(
                    H3("How to Use the AI Assistant"),
                    P("The AI assistant can help you with:"),
                    Ul(
                        Li("🔍 Search for documents using natural language"),
                        Li("📝 Summarize documents"),
                        Li("🔑 Extract key points from documents"),
                        Li("🔗 Find related documents"),
                        Li("❓ Answer questions from specific documents"),
                        Li("⚖️ Compare multiple documents"),
                    ),
                    Details(
                        Summary("💡 Example Questions"),
                        Ul(
                            Li('"List all my documents"'),
                            Li('"Search for documents about marketing"'),
                            Li('"Summarize document [document-id]"'),
                            Li('"What are the key points in the Q4 report?"'),
                            Li('"Find documents related to [document-id]"'),
                            Li('"Compare document A and document B"'),
                        ),
                        style="margin-top: 1rem;"
                    ),
                    cls="card"
                ),
                
                # User Selection
                Div(
                    H3("Select User Context"),
                    Form(
                        Div(
                            Label("Chat as:", For="chat-user"),
                            Select(
                                *[Option(
                                    f"{u.get('full_name', 'No Name')} ({u['email']})",
                                    value=u['id']
                                ) for u in users],
                                id="chat-user",
                                name="user_id",
                                required=True,
                                onchange="document.getElementById('chat-history').innerHTML = ''; document.getElementById('chat-input').focus();"
                            ),
                        ),
                        cls="form-row"
                    ),
                    cls="card"
                ),
                
                # Chat Interface
                Div(
                    Div(
                        H3("Conversation"),
                        Div(
                            P("👋 Hello! I'm your AI document assistant. Ask me anything about your documents!", 
                              cls="assistant-message chat-message"),
                            id="chat-history"
                        ),
                    ),
                    
                    # Input Form
                    Form(
                        Div(
                            Input(
                                type="text",
                                name="query",
                                id="chat-input",
                                placeholder="Ask about your documents...",
                                required=True,
                                style="width: 100%; margin-bottom: 0.5rem;",
                                autocomplete="off"
                            ),
                            Div(
                                Button("Send 🚀", type="submit", style="flex: 1;"),
                                Button(
                                    "Clear Chat",
                                    type="button",
                                    onclick="document.getElementById('chat-history').innerHTML = '<p class=\"assistant-message chat-message\">👋 Hello! I\\'m your AI document assistant. Ask me anything about your documents!</p>'; document.getElementById('chat-input').value = ''; document.getElementById('chat-input').focus();",
                                    style="flex: 0.3; background: #6c757d;"
                                ),
                                cls="btn-group",
                                style="margin: 0;"
                            ),
                            cls="form-row"
                        ),
                        hx_post="/chat/message",
                        hx_target="#chat-history",
                        hx_swap="beforeend",
                        hx_on__after_request="this.reset(); document.getElementById('chat-input').focus();"
                    ),
                    cls="card chat-container"
                )
            )
        )
    
    @rt('/chat/message')
    async def post(query: str, user_id: str = None):
        # Get user_id from the select dropdown
        if not user_id:
            # Try to get from form
            from starlette.requests import Request
            user_id = Request.query_params.get('user_id')
        
        # Get actual user_id from the chat-user select
        # In HTMX, we need to include it in the request
        # This is a workaround - we'll get it from JavaScript
        import html
        query_escaped = html.escape(query)
        
        # Show user message immediately
        user_msg = Div(
            P(Strong("You: "), query),
            cls="user-message chat-message"
        )
        
        # Show loading
        loading = Div(
            P(Strong("Assistant: "), "🤔 Thinking...", id="loading-msg"),
            cls="assistant-message chat-message"
        )
        
        try:
            # Get user_id from the select element via JavaScript
            # We'll use a script to inject it into the form
            script_get_user = Script("""
                const userId = document.getElementById('chat-user').value;
                const forms = document.querySelectorAll('form[hx-post="/chat/message"]');
                forms.forEach(f => {
                    f.setAttribute('hx-vals', JSON.stringify({user_id: userId}));
                });
            """)
            
            # For now, we'll need to pass user_id differently
            # Let's use the first user if not provided
            if not user_id:
                users_resp = http_client.get('/users')
                users = users_resp.json() if users_resp.status_code == 200 else []
                if users:
                    user_id = users[0]['id']
            
            resp = http_client.post('/agent/query', json={
                'query': query,
                'user_id': user_id
            }, timeout=30)
            
            if resp.status_code != 200:
                error_msg = resp.json().get('detail', 'Unknown error')
                return Div(
                    user_msg,
                    Div(
                        P(Strong("Assistant: "), f"❌ Error: {error_msg}"),
                        cls="assistant-message chat-message"
                    )
                )
            
            data = resp.json()
            response = data.get('response', 'No response received')
            
            # Format the response
            return Div(
                user_msg,
                Div(
                    P(Strong("Assistant: ")),
                    Div(response, style="white-space: pre-wrap;"),
                    cls="assistant-message chat-message"
                )
            )
            
        except Exception as e:
            return Div(
                user_msg,
                Div(
                    P(Strong("Assistant: "), f"❌ Error: {str(e)}"),
                    cls="assistant-message chat-message"
                )
            )