from fasthtml.common import *
import httpx
from typing import Optional
import sys
import os

# Add parent directory to path to import shared modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.layout import base_layout
from shared.styles import PERMISSION_STYLES

API_BASE = "http://localhost:8000"

def permissions_page_layout(content):
    """Common layout for permissions pages"""
    return base_layout(
        "Permissions - Document Control System",
        content,
        additional_styles=PERMISSION_STYLES
    )

def _old_permissions_page_layout(content):
    """DEPRECATED - keeping temporarily for reference"""
    return Html(
        Head(
            Title("Permissions - Document Control System"),
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
                .btn-danger {
                    background: #dc3545;
                }
                .btn-danger:hover {
                    background: #c82333;
                }
                .btn-small {
                    padding: 5px 10px;
                    font-size: 12px;
                }
                .content {
                    background: white;
                    padding: 30px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }
                .permission-list {
                    list-style: none;
                    padding: 0;
                }
                .permission-item {
                    padding: 15px;
                    border-bottom: 1px solid #e9ecef;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                }
                .permission-item:last-child {
                    border-bottom: none;
                }
                .permission-info {
                    flex-grow: 1;
                }
                .permission-info h4 {
                    margin: 0 0 5px 0;
                    color: #333;
                }
                .permission-info p {
                    margin: 0;
                    color: #666;
                    font-size: 14px;
                }
                .permission-actions {
                    display: flex;
                    gap: 10px;
                }
                .form-group {
                    margin-bottom: 20px;
                }
                .form-group label {
                    display: block;
                    margin-bottom: 5px;
                    font-weight: bold;
                    color: #333;
                }
                .form-group input, .form-group select {
                    width: 100%;
                    padding: 10px;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    font-size: 14px;
                    box-sizing: border-box;
                }
                .form-group input:focus, .form-group select:focus {
                    outline: none;
                    border-color: #007bff;
                }
                .error {
                    color: #dc3545;
                    padding: 10px;
                    background: #f8d7da;
                    border-radius: 4px;
                    margin-bottom: 20px;
                }
                .success {
                    color: #155724;
                    padding: 10px;
                    background: #d4edda;
                    border-radius: 4px;
                    margin-bottom: 20px;
                }
                .empty-state {
                    text-align: center;
                    padding: 40px;
                    color: #666;
                }
                .badge {
                    display: inline-block;
                    padding: 4px 10px;
                    border-radius: 4px;
                    font-size: 12px;
                    font-weight: bold;
                }
                .badge-read {
                    background: #17a2b8;
                    color: white;
                }
                .badge-write {
                    background: #ffc107;
                    color: #333;
                }
                .badge-admin {
                    background: #dc3545;
                    color: white;
                }
                .section {
                    margin-bottom: 30px;
                }
                .section h3 {
                    color: #333;
                    border-bottom: 2px solid #007bff;
                    padding-bottom: 10px;
                    margin-bottom: 20px;
                }
                .info-box {
                    background: #e7f3ff;
                    padding: 15px;
                    border-radius: 4px;
                    margin-bottom: 20px;
                    border-left: 4px solid #007bff;
                }
                .info-box p {
                    margin: 5px 0;
                    color: #333;
                }
                .tabs {
                    display: flex;
                    gap: 10px;
                    margin-bottom: 20px;
                    border-bottom: 2px solid #e9ecef;
                }
                .tab {
                    padding: 10px 20px;
                    background: none;
                    border: none;
                    border-bottom: 3px solid transparent;
                    cursor: pointer;
                    color: #666;
                    text-decoration: none;
                    font-size: 14px;
                }
                .tab:hover {
                    color: #007bff;
                }
                .tab.active {
                    color: #007bff;
                    border-bottom-color: #007bff;
                }
            """)
        ),
        Body(content)
    )

async def get_documents():
    """Fetch all documents from API"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{API_BASE}/documents")
            response.raise_for_status()
            return response.json()
    except Exception as e:
        print(f"Error fetching documents: {e}")
        return []

async def get_document_by_id(document_id: str):
    """Fetch a specific document by ID"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{API_BASE}/documents/{document_id}")
            response.raise_for_status()
            return response.json()
    except Exception as e:
        print(f"Error fetching document: {e}")
        return None

async def get_users():
    """Fetch all users from API"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{API_BASE}/users")
            response.raise_for_status()
            return response.json()
    except Exception as e:
        print(f"Error fetching users: {e}")
        return []

async def get_document_permissions(document_id: str):
    """Fetch permissions for a specific document"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{API_BASE}/documents/{document_id}/permissions")
            response.raise_for_status()
            return response.json()
    except Exception as e:
        print(f"Error fetching permissions: {e}")
        return []

async def grant_permission(document_id: str, user_id: str, permission_type: str):
    """Grant a permission to a user for a document"""
    try:
        async with httpx.AsyncClient() as client:
            data = {
                "document_id": document_id,
                "user_id": user_id,
                "permission_type": permission_type
            }
            response = await client.post(f"{API_BASE}/permissions", json=data)
            response.raise_for_status()
            return response.json(), None
    except httpx.HTTPStatusError as e:
        error_msg = e.response.text
        try:
            error_json = e.response.json()
            error_msg = error_json.get("detail", error_msg)
        except:
            pass
        return None, f"Error: {error_msg}"
    except Exception as e:
        return None, f"Error granting permission: {str(e)}"

async def revoke_permission(permission_id: str):
    """Revoke a permission"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.delete(f"{API_BASE}/permissions/{permission_id}")
            response.raise_for_status()
            return response.json(), None
    except httpx.HTTPStatusError as e:
        return None, f"Error: {e.response.text}"
    except Exception as e:
        return None, f"Error revoking permission: {str(e)}"

def get_badge_class(permission_type: str):
    """Get the CSS class for a permission badge"""
    if permission_type == "read":
        return "badge badge-read"
    elif permission_type == "write":
        return "badge badge-write"
    elif permission_type == "admin":
        return "badge badge-admin"
    return "badge"

def render_permissions_main(documents, error=None, success=None, mode="grant"):
    """Render the main permissions page with tabs"""
    return permissions_page_layout(
        Div(
            Div(
                H1("Permissions Management"),
                Div(
                    A("Back to Home", href="/", cls="btn btn-secondary"),
                ),
                cls="header"
            ),

            Div(
                error and Div(error, cls="error") or None,
                success and Div(success, cls="success") or None,

                # Tabs
                Div(
                    A("Grant Permission", href="/permissions?mode=grant", cls=f"tab {'active' if mode == 'grant' else ''}"),
                    A("View by Document", href="/permissions?mode=view", cls=f"tab {'active' if mode == 'view' else ''}"),
                    cls="tabs"
                ),

                # Content based on mode
                mode == "grant" and render_grant_form(documents) or render_view_documents(documents),

                cls="content"
            )
        )
    )

def render_grant_form(documents):
    """Render the grant permission form"""
    return Div(
        Div(
            P("Grant read, write, or admin permissions to users for specific documents."),
            P(Strong("Permission Types:")),
            Ul(
                Li(Span("read", cls="badge badge-read"), " - Read-only access"),
                Li(Span("write", cls="badge badge-write"), " - Read and write access"),
                Li(Span("admin", cls="badge badge-admin"), " - Full administrative access")
            ),
            cls="info-box"
        ),

        H3("Grant New Permission"),

        Form(
            Div(
                Label("Select Document", _for="document_id"),
                Select(
                    Option("-- Select a document --", value="", selected=True, disabled=True),
                    *[Option(f"{doc.get('title')} ({doc.get('status')})", value=doc.get('id')) for doc in documents],
                    name="document_id",
                    id="document_id",
                    required=True,
                    onchange="window.location.href='/permissions/grant?document_id=' + this.value"
                ),
                cls="form-group"
            ),

            P("Select a document to continue", style="color: #666; font-style: italic;"),

            method="GET",
            action="/permissions/grant"
        ),
        cls="section"
    )

def render_view_documents(documents):
    """Render the view permissions by document list"""
    return Div(
        H3("View Permissions by Document"),

        documents and Ul(
            *[Li(
                Div(
                    Div(
                        H4(doc.get("title")),
                        P(f"Status: {doc.get('status')} | Created: {doc.get('created_at', 'N/A')[:10]}"),
                        cls="permission-info"
                    ),
                    Div(
                        A("View Permissions", href=f"/permissions/document/{doc['id']}", cls="btn btn-small"),
                        cls="permission-actions"
                    ),
                    cls="permission-item"
                )
            ) for doc in documents],
            cls="permission-list"
        ) or Div(
            P("No documents found."),
            cls="empty-state"
        ),
        cls="section"
    )

def render_grant_permission_form(document, users, selected_user_id=None, error=None, success=None):
    """Render the permission grant form for a specific document"""
    if not document:
        return permissions_page_layout(
            Div(
                Div(
                    H1("Document Not Found"),
                    A("Back to Permissions", href="/permissions", cls="btn btn-secondary"),
                    cls="header"
                ),
                Div(
                    P("The requested document could not be found."),
                    cls="content"
                )
            )
        )

    return permissions_page_layout(
        Div(
            Div(
                H1("Grant Permission"),
                Div(
                    A("Back to Permissions", href="/permissions", cls="btn btn-secondary"),
                ),
                cls="header"
            ),

            Div(
                error and Div(error, cls="error") or None,
                success and Div(success, cls="success") or None,

                Div(
                    H3("Document Information"),
                    P(Strong("Title: "), document.get("title")),
                    P(Strong("Status: "), document.get("status")),
                    P(Strong("Description: "), document.get("description") or "N/A"),
                    cls="info-box"
                ),

                H3("Grant Permission to User"),

                Form(
                    Input(type="hidden", name="document_id", value=document.get("id")),

                    Div(
                        Label("Select User", _for="user_id"),
                        Select(
                            Option("-- Select a user --", value="", selected=not selected_user_id, disabled=True),
                            *[Option(
                                f"{user.get('email')} ({user.get('full_name') or 'No name'})",
                                value=user.get('id'),
                                selected=(selected_user_id == user.get('id'))
                            ) for user in users],
                            name="user_id",
                            id="user_id",
                            required=True
                        ),
                        cls="form-group"
                    ),

                    Div(
                        Label("Permission Type", _for="permission_type"),
                        Select(
                            Option("read - Read-only access", value="read", selected=True),
                            Option("write - Read and write access", value="write"),
                            Option("admin - Full administrative access", value="admin"),
                            name="permission_type",
                            id="permission_type",
                            required=True
                        ),
                        cls="form-group"
                    ),

                    Div(
                        Button("Cancel", type="button", onclick="window.location.href='/permissions'", cls="btn btn-secondary"),
                        Button("Grant Permission", type="submit", cls="btn"),
                        style="display: flex; gap: 10px; justify-content: flex-end;"
                    ),

                    method="POST",
                    action="/permissions/grant"
                ),

                cls="content"
            )
        )
    )

def render_document_permissions(document, permissions, users_map, error=None, success=None):
    """Render permissions for a specific document"""
    if not document:
        return permissions_page_layout(
            Div(
                Div(
                    H1("Document Not Found"),
                    A("Back to Permissions", href="/permissions", cls="btn btn-secondary"),
                    cls="header"
                ),
                Div(
                    P("The requested document could not be found."),
                    cls="content"
                )
            )
        )

    return permissions_page_layout(
        Div(
            Div(
                H1(f"Permissions: {document.get('title')}"),
                Div(
                    A("Back to Permissions", href="/permissions?mode=view", cls="btn btn-secondary"),
                    A("Grant New Permission", href=f"/permissions/grant?document_id={document.get('id')}", cls="btn"),
                ),
                cls="header"
            ),

            Div(
                error and Div(error, cls="error") or None,
                success and Div(success, cls="success") or None,

                Div(
                    H3("Document Information"),
                    P(Strong("Title: "), document.get("title")),
                    P(Strong("Status: "), document.get("status")),
                    P(Strong("Created: "), document.get("created_at", "N/A")[:10]),
                    cls="info-box"
                ),

                Div(
                    H3(f"Permissions ({len(permissions)})"),

                    permissions and Ul(
                        *[Li(
                            Div(
                                Div(
                                    H4(users_map.get(perm.get("user_id"), {}).get("email", "Unknown User")),
                                    P(f"User: {users_map.get(perm.get('user_id'), {}).get('full_name', 'N/A')}"),
                                    P(f"Granted: {perm.get('granted_at', 'N/A')[:10]}"),
                                    cls="permission-info"
                                ),
                                Div(
                                    Span(perm.get("permission_type"), cls=get_badge_class(perm.get("permission_type"))),
                                    Form(
                                        Input(type="hidden", name="permission_id", value=perm.get("id")),
                                        Input(type="hidden", name="document_id", value=document.get("id")),
                                        Button("Revoke", type="submit", cls="btn btn-danger btn-small"),
                                        method="POST",
                                        action="/permissions/revoke",
                                        style="display: inline;"
                                    ),
                                    cls="permission-actions"
                                ),
                                cls="permission-item"
                            )
                        ) for perm in permissions],
                        cls="permission-list"
                    ) or Div(
                        P("No permissions granted for this document yet."),
                        A("Grant a permission", href=f"/permissions/grant?document_id={document.get('id')}", cls="btn"),
                        cls="empty-state"
                    ),
                    cls="section"
                ),

                cls="content"
            )
        )
    )
