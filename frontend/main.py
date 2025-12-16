from fasthtml.common import *
import httpx
from pages.users import (
    get_users, get_user_by_id, create_user, update_user,
    render_users_list, render_user_form, render_user_details
)

# Create FastHTML app
app, rt = fast_app()

# Backend API base URL
API_BASE = "http://localhost:8000"

# Simple in-memory user session (for demo purposes)
CURRENT_USER_ID = None

@rt("/")
def get():
    """Main landing page with navigation to key features"""
    return Html(
        Head(
            Title("Document Control System"),
            Style("""
                body {
                    font-family: Arial, sans-serif;
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 20px;
                    background: #f5f5f5;
                }
                .hero {
                    background: white;
                    padding: 40px;
                    border-radius: 8px;
                    margin-bottom: 30px;
                    text-align: center;
                }
                .features {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                    gap: 20px;
                    margin-top: 30px;
                }
                .feature-card {
                    background: white;
                    padding: 30px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    transition: transform 0.2s;
                }
                .feature-card:hover {
                    transform: translateY(-5px);
                    box-shadow: 0 4px 8px rgba(0,0,0,0.15);
                }
                .feature-card h2 {
                    margin-top: 0;
                    color: #333;
                }
                .feature-card p {
                    color: #666;
                    line-height: 1.6;
                }
                .btn {
                    display: inline-block;
                    padding: 10px 20px;
                    background: #007bff;
                    color: white;
                    text-decoration: none;
                    border-radius: 4px;
                    margin-top: 10px;
                    border: none;
                    cursor: pointer;
                }
                .btn:hover {
                    background: #0056b3;
                }
                .user-section {
                    background: #e9ecef;
                    padding: 15px;
                    border-radius: 4px;
                    margin-bottom: 20px;
                }
            """)
        ),
        Body(
            Div(
                H1("Document Control System"),
                P("Manage documents with version control, permissions, and AI-powered search"),
                cls="hero"
            ),

            Div(
                H3("Current User Session"),
                P("Select or create a user to interact with the system"),
                A("Manage Users", href="/users", cls="btn"),
                cls="user-section"
            ),

            Div(
                # Documents Feature
                Div(
                    H2("Documents"),
                    P("Create, view, and manage documents with version control. Upload PDFs or create documents from scratch."),
                    A("View Documents", href="/documents", cls="btn"),
                    cls="feature-card"
                ),

                # Upload Feature
                Div(
                    H2("Upload PDF"),
                    P("Upload PDF files to create new documents or add versions to existing documents."),
                    A("Upload PDF", href="/upload", cls="btn"),
                    cls="feature-card"
                ),

                # Search Feature
                Div(
                    H2("Search"),
                    P("Search through document content using RAG (Retrieval Augmented Generation) technology."),
                    A("Search Documents", href="/search", cls="btn"),
                    cls="feature-card"
                ),

                # AI Agent Feature
                Div(
                    H2("AI Agent"),
                    P("Ask questions about your documents and get intelligent responses powered by AI."),
                    A("Query AI Agent", href="/agent", cls="btn"),
                    cls="feature-card"
                ),

                # Users Feature
                Div(
                    H2("Users"),
                    P("Manage users and view their documents and permissions."),
                    A("Manage Users", href="/users", cls="btn"),
                    cls="feature-card"
                ),

                # Permissions Feature
                Div(
                    H2("Permissions"),
                    P("Control document access by granting read, write, or admin permissions to users."),
                    A("Manage Permissions", href="/permissions", cls="btn"),
                    cls="feature-card"
                ),

                cls="features"
            )
        )
    )

@rt("/documents")
def get():
    """Documents listing page placeholder"""
    return Html(
        Head(Title("Documents")),
        Body(
            H1("Documents"),
            P("Document listing will be implemented here"),
            A("Back to Home", href="/"),
            Hr(),
            P("Features to implement:"),
            Ul(
                Li("List all documents (GET /documents)"),
                Li("Filter by status"),
                Li("View document details"),
                Li("Create new document"),
                Li("Update document metadata"),
                Li("Archive documents")
            )
        )
    )

@rt("/upload")
def get():
    """PDF upload page placeholder"""
    return Html(
        Head(Title("Upload PDF")),
        Body(
            H1("Upload PDF"),
            P("PDF upload functionality will be implemented here"),
            A("Back to Home", href="/"),
            Hr(),
            P("Features to implement:"),
            Ul(
                Li("Upload PDF to existing document (POST /documents/{id}/upload-pdf)"),
                Li("Create document from PDF (POST /documents/create-from-pdf)"),
                Li("Show upload progress"),
                Li("Display version information")
            )
        )
    )

@rt("/search")
def get():
    """Search page placeholder"""
    return Html(
        Head(Title("Search Documents")),
        Body(
            H1("Search Documents"),
            P("RAG-based search will be implemented here"),
            A("Back to Home", href="/"),
            Hr(),
            P("Features to implement:"),
            Ul(
                Li("Search form with query input (POST /search)"),
                Li("Display search results with relevance scores"),
                Li("Link to source documents"),
                Li("Show content snippets")
            )
        )
    )

@rt("/agent")
def get():
    """AI Agent query page placeholder"""
    return Html(
        Head(Title("AI Agent")),
        Body(
            H1("AI Agent"),
            P("AI-powered document queries will be implemented here"),
            A("Back to Home", href="/"),
            Hr(),
            P("Features to implement:"),
            Ul(
                Li("Query input form (POST /agent/query)"),
                Li("Display AI responses"),
                Li("Show referenced documents"),
                Li("Chat-like interface")
            )
        )
    )

@rt("/users")
async def get():
    """Users list page"""
    users = await get_users()
    return render_users_list(users)

@rt("/users/create")
def get():
    """Create user form"""
    return render_user_form("Create New User", "/users/create")

@rt("/users/create")
async def post(email: str, full_name: str = "", role: str = ""):
    """Handle user creation"""
    user, error = await create_user(
        email=email,
        full_name=full_name or None,
        role=role or None
    )

    if error:
        return render_user_form("Create New User", "/users/create", error=error)

    # Redirect to users list with success message
    users = await get_users()
    return render_users_list(users, success="User created successfully!")

@rt("/users/{user_id}")
async def get(user_id: str):
    """User details page"""
    user = await get_user_by_id(user_id)
    return render_user_details(user)

@rt("/users/{user_id}/edit")
async def get(user_id: str):
    """Edit user form"""
    user = await get_user_by_id(user_id)
    if not user:
        users = await get_users()
        return render_users_list(users, error="User not found")
    return render_user_form("Edit User", f"/users/{user_id}/edit", user=user)

@rt("/users/{user_id}/edit")
async def post(user_id: str, email: str = "", full_name: str = "", role: str = ""):
    """Handle user update"""
    user, error = await update_user(
        user_id=user_id,
        email=email or None,
        full_name=full_name or None,
        role=role or None
    )

    if error:
        existing_user = await get_user_by_id(user_id)
        return render_user_form("Edit User", f"/users/{user_id}/edit", user=existing_user, error=error)

    # Redirect to user details
    updated_user = await get_user_by_id(user_id)
    return render_user_details(updated_user)

@rt("/permissions")
def get():
    """Permissions management page placeholder"""
    return Html(
        Head(Title("Permissions")),
        Body(
            H1("Permissions"),
            P("Permission management will be implemented here"),
            A("Back to Home", href="/"),
            Hr(),
            P("Features to implement:"),
            Ul(
                Li("Grant permissions (POST /permissions)"),
                Li("List document permissions (GET /documents/{id}/permissions)"),
                Li("Revoke permissions (DELETE /permissions/{id})"),
                Li("Permission types: read, write, admin")
            )
        )
    )

# Run the app
serve()
