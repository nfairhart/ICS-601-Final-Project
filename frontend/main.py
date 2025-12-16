from fasthtml.common import *
from frontend.pages.home import register as register_home
from frontend.pages.users import register as register_users
from frontend.pages.documents import register as register_documents
from frontend.pages.search import register as register_search
from frontend.pages.chat import register as register_chat


app, rt = fast_app(
    hdrs=(
        Link(rel='stylesheet', href='https://cdn.jsdelivr.net/npm/water.css@2/out/water.css'),
        Style("""
            .chat-container { max-width: 900px; margin: 0 auto; }
            .chat-message { padding: 1rem; margin: 0.5rem 0; border-radius: 8px; }
            .user-message { background: #e3f2fd; margin-left: 2rem; }
            .assistant-message { background: #f5f5f5; margin-right: 2rem; }
            .tool-call { background: #fff3e0; padding: 0.5rem; margin: 0.5rem 0; border-left: 3px solid #ff9800; font-size: 0.9em; }
            .card { background: white; padding: 1.5rem; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin: 1rem 0; }
            .badge { display: inline-block; padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.85em; font-weight: 600; }
            .badge-draft { background: #fff3cd; color: #856404; }
            .badge-active { background: #d4edda; color: #155724; }
            .badge-archived { background: #d6d8db; color: #383d41; }
            .form-row { margin-bottom: 1rem; }
            .form-row label { display: block; margin-bottom: 0.25rem; font-weight: 600; }
            .btn-group { display: flex; gap: 0.5rem; margin-top: 1rem; }
            .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin: 1rem 0; }
            .stat-card { padding: 1rem; border-left: 4px solid #0066cc; background: #f8f9fa; }
            .htmx-indicator { display: none; }
            .htmx-request .htmx-indicator { display: block; }
        """)
    )
)

# Register routes from pages
register_home(rt)
register_users(rt)
register_documents(rt)
register_search(rt)
register_chat(rt)

serve()