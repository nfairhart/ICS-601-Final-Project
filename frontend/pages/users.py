from fasthtml.common import *
import httpx
from typing import Optional

API_BASE = "http://localhost:8000"

def users_page_layout(content):
    """Common layout for users pages"""
    return Html(
        Head(
            Title("Users - Document Control System"),
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
                .content {
                    background: white;
                    padding: 30px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }
                .user-list {
                    list-style: none;
                    padding: 0;
                }
                .user-item {
                    padding: 15px;
                    border-bottom: 1px solid #e9ecef;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                }
                .user-item:last-child {
                    border-bottom: none;
                }
                .user-info {
                    flex-grow: 1;
                }
                .user-info h3 {
                    margin: 0 0 5px 0;
                    color: #333;
                }
                .user-info p {
                    margin: 0;
                    color: #666;
                    font-size: 14px;
                }
                .user-actions {
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
                .form-group input {
                    width: 100%;
                    padding: 10px;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    font-size: 14px;
                    box-sizing: border-box;
                }
                .form-group input:focus {
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
                .user-details {
                    margin-top: 20px;
                }
                .detail-section {
                    margin-bottom: 30px;
                }
                .detail-section h3 {
                    color: #333;
                    border-bottom: 2px solid #007bff;
                    padding-bottom: 10px;
                }
                .detail-row {
                    display: flex;
                    padding: 10px 0;
                    border-bottom: 1px solid #e9ecef;
                }
                .detail-label {
                    font-weight: bold;
                    width: 150px;
                    color: #555;
                }
                .detail-value {
                    color: #333;
                }
                .badge {
                    display: inline-block;
                    padding: 4px 8px;
                    background: #007bff;
                    color: white;
                    border-radius: 4px;
                    font-size: 12px;
                }
            """)
        ),
        Body(content)
    )

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

async def get_user_by_id(user_id: str):
    """Fetch a specific user by ID"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{API_BASE}/users/{user_id}")
            response.raise_for_status()
            return response.json()
    except Exception as e:
        print(f"Error fetching user: {e}")
        return None

async def create_user(email: str, full_name: Optional[str] = None, role: Optional[str] = None):
    """Create a new user"""
    try:
        async with httpx.AsyncClient() as client:
            data = {"email": email}
            if full_name:
                data["full_name"] = full_name
            if role:
                data["role"] = role

            response = await client.post(f"{API_BASE}/users", json=data)
            response.raise_for_status()
            return response.json(), None
    except httpx.HTTPStatusError as e:
        return None, f"Error: {e.response.text}"
    except Exception as e:
        return None, f"Error creating user: {str(e)}"

async def update_user(user_id: str, email: Optional[str] = None,
                     full_name: Optional[str] = None, role: Optional[str] = None):
    """Update a user"""
    try:
        async with httpx.AsyncClient() as client:
            data = {}
            if email:
                data["email"] = email
            if full_name:
                data["full_name"] = full_name
            if role:
                data["role"] = role

            response = await client.patch(f"{API_BASE}/users/{user_id}", json=data)
            response.raise_for_status()
            return response.json(), None
    except httpx.HTTPStatusError as e:
        return None, f"Error: {e.response.text}"
    except Exception as e:
        return None, f"Error updating user: {str(e)}"

def render_users_list(users, error=None, success=None):
    """Render the users list view"""
    return users_page_layout(
        Div(
            Div(
                H1("Users"),
                Div(
                    A("Back to Home", href="/", cls="btn btn-secondary"),
                    A("Create New User", href="/users/create", cls="btn"),
                ),
                cls="header"
            ),

            Div(
                error and Div(error, cls="error") or None,
                success and Div(success, cls="success") or None,

                H2(f"All Users ({len(users)})"),

                users and Ul(
                    *[Li(
                        Div(
                            Div(
                                H3(user.get("full_name") or user.get("email")),
                                P(f"Email: {user.get('email')}"),
                                P(f"Role: {user.get('role') or 'N/A'}"),
                                cls="user-info"
                            ),
                            Div(
                                A("View Details", href=f"/users/{user['id']}", cls="btn"),
                                A("Edit", href=f"/users/{user['id']}/edit", cls="btn btn-secondary"),
                                cls="user-actions"
                            ),
                            cls="user-item"
                        )
                    ) for user in users],
                    cls="user-list"
                ) or Div(
                    P("No users found."),
                    A("Create your first user", href="/users/create", cls="btn"),
                    cls="empty-state"
                ),
                cls="content"
            )
        )
    )

def render_user_form(title, action, user=None, error=None):
    """Render user creation/edit form"""
    return users_page_layout(
        Div(
            Div(
                H1(title),
                A("Back to Users", href="/users", cls="btn btn-secondary"),
                cls="header"
            ),

            Div(
                error and Div(error, cls="error") or None,

                Form(
                    Div(
                        Label("Email (required)", _for="email"),
                        Input(
                            type="email",
                            name="email",
                            id="email",
                            value=user.get("email") if user else "",
                            required=True
                        ),
                        cls="form-group"
                    ),

                    Div(
                        Label("Full Name", _for="full_name"),
                        Input(
                            type="text",
                            name="full_name",
                            id="full_name",
                            value=user.get("full_name") if user else ""
                        ),
                        cls="form-group"
                    ),

                    Div(
                        Label("Role", _for="role"),
                        Input(
                            type="text",
                            name="role",
                            id="role",
                            value=user.get("role") if user else "",
                            placeholder="e.g., editor, admin, viewer"
                        ),
                        cls="form-group"
                    ),

                    Div(
                        Button("Cancel", type="button", onclick="window.location.href='/users'", cls="btn btn-secondary"),
                        Button("Save User", type="submit", cls="btn"),
                        style="display: flex; gap: 10px; justify-content: flex-end;"
                    ),

                    method="POST",
                    action=action
                ),
                cls="content"
            )
        )
    )

def render_user_details(user, error=None):
    """Render user details view"""
    if not user:
        return users_page_layout(
            Div(
                Div(
                    H1("User Not Found"),
                    A("Back to Users", href="/users", cls="btn btn-secondary"),
                    cls="header"
                ),
                Div(
                    P("The requested user could not be found."),
                    cls="content"
                )
            )
        )

    return users_page_layout(
        Div(
            Div(
                H1(user.get("full_name") or user.get("email")),
                Div(
                    A("Back to Users", href="/users", cls="btn btn-secondary"),
                    A("Edit User", href=f"/users/{user['id']}/edit", cls="btn"),
                ),
                cls="header"
            ),

            Div(
                error and Div(error, cls="error") or None,

                Div(
                    H2("User Information"),
                    Div(
                        Div(Span("ID:", cls="detail-label"), Span(user.get("id"), cls="detail-value"), cls="detail-row"),
                        Div(Span("Email:", cls="detail-label"), Span(user.get("email"), cls="detail-value"), cls="detail-row"),
                        Div(Span("Full Name:", cls="detail-label"), Span(user.get("full_name") or "N/A", cls="detail-value"), cls="detail-row"),
                        Div(Span("Role:", cls="detail-label"), Span(user.get("role") or "N/A", cls="detail-value"), cls="detail-row"),
                        Div(Span("Created At:", cls="detail-label"), Span(user.get("created_at"), cls="detail-value"), cls="detail-row"),
                        Div(Span("Updated At:", cls="detail-label"), Span(user.get("updated_at"), cls="detail-value"), cls="detail-row"),
                    ),
                    cls="detail-section"
                ),

                Div(
                    H3("Documents Created"),
                    user.get("documents") and len(user.get("documents")) > 0 and Ul(
                        *[Li(
                            f"{doc.get('title')} ({doc.get('status')})"
                        ) for doc in user.get("documents", [])]
                    ) or P("No documents created yet.", style="color: #666;"),
                    cls="detail-section"
                ),

                Div(
                    H3("Document Permissions"),
                    user.get("permissions") and len(user.get("permissions")) > 0 and Ul(
                        *[Li(
                            Span(f"Document ID: {perm.get('document_id')}", style="margin-right: 10px;"),
                            Span(perm.get('permission_type'), cls="badge")
                        ) for perm in user.get("permissions", [])]
                    ) or P("No permissions granted yet.", style="color: #666;"),
                    cls="detail-section"
                ),

                cls="content"
            )
        )
    )
