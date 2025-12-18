from fasthtml.common import *
import httpx
from typing import Optional
import sys
import os

# Add parent directory to path to import shared modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.layout import base_layout

API_BASE = "http://localhost:8000"

def users_page_layout(content):
    """Common layout for users pages"""
    return base_layout(
        "Users - Document Control System",
        content
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
    """
    Create a new user.
    Validates input and handles Pydantic validation errors from backend.
    """
    try:
        async with httpx.AsyncClient() as client:
            data = {"email": email.strip()}
            if full_name and full_name.strip():
                data["full_name"] = full_name.strip()
            if role and role.strip():
                data["role"] = role.strip()

            response = await client.post(f"{API_BASE}/users", json=data)
            response.raise_for_status()
            return response.json(), None
    except httpx.HTTPStatusError as e:
        # Parse validation errors if available
        try:
            error_data = e.response.json()
            if "detail" in error_data and isinstance(error_data["detail"], list):
                errors = [f"{err['loc'][-1]}: {err['msg']}" for err in error_data["detail"]]
                return None, "Validation errors: " + "; ".join(errors)
            return None, f"Error: {error_data.get('detail', e.response.text)}"
        except:
            return None, f"Error: {e.response.text}"
    except Exception as e:
        return None, f"Error creating user: {str(e)}"

async def update_user(user_id: str, email: Optional[str] = None,
                     full_name: Optional[str] = None, role: Optional[str] = None):
    """
    Update a user.
    Validates input and handles Pydantic validation errors from backend.
    """
    try:
        async with httpx.AsyncClient() as client:
            data = {}
            if email and email.strip():
                data["email"] = email.strip()
            if full_name is not None:
                # Send trimmed value or None if empty
                data["full_name"] = full_name.strip() if full_name.strip() else None
            if role and role.strip():
                data["role"] = role.strip()

            if not data:
                return None, "No fields to update"

            response = await client.patch(f"{API_BASE}/users/{user_id}", json=data)
            response.raise_for_status()
            return response.json(), None
    except httpx.HTTPStatusError as e:
        # Parse validation errors if available
        try:
            error_data = e.response.json()
            if "detail" in error_data and isinstance(error_data["detail"], list):
                errors = [f"{err['loc'][-1]}: {err['msg']}" for err in error_data["detail"]]
                return None, "Validation errors: " + "; ".join(errors)
            return None, f"Error: {error_data.get('detail', e.response.text)}"
        except:
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
                        Select(
                            Option("-- Select Role (Optional) --", value="", selected=(not user or not user.get("role"))),
                            Option("Viewer", value="viewer", selected=(user and user.get("role") == "viewer")),
                            Option("Editor", value="editor", selected=(user and user.get("role") == "editor")),
                            Option("Admin", value="admin", selected=(user and user.get("role") == "admin")),
                            Option("Owner", value="owner", selected=(user and user.get("role") == "owner")),
                            name="role",
                            id="role"
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
