from fasthtml.common import *
import httpx
from typing import Optional
import sys
import os

# Add parent directory to path to import shared modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.layout import base_layout
from shared.styles import DOCUMENT_STYLES

API_BASE = "http://localhost:8000"

def documents_page_layout(content):
    """Common layout for documents pages"""
    return base_layout(
        "Documents - Document Control System",
        content,
        additional_styles=DOCUMENT_STYLES
    )

async def get_documents(status: Optional[str] = None):
    """Fetch all documents from API with optional status filter"""
    try:
        async with httpx.AsyncClient() as client:
            url = f"{API_BASE}/documents"
            if status:
                url += f"?status={status}"
            response = await client.get(url)
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

async def create_document(title: str, created_by: str, description: Optional[str] = None):
    """Create a new document"""
    try:
        async with httpx.AsyncClient() as client:
            data = {
                "title": title,
                "created_by": created_by
            }
            if description:
                data["description"] = description

            response = await client.post(f"{API_BASE}/documents", json=data)
            response.raise_for_status()
            return response.json(), None
    except httpx.HTTPStatusError as e:
        return None, f"Error: {e.response.text}"
    except Exception as e:
        return None, f"Error creating document: {str(e)}"

async def update_document(document_id: str, title: Optional[str] = None,
                         status: Optional[str] = None, description: Optional[str] = None):
    """
    Update a document.
    Sends data as JSON body to match backend Pydantic schema validation.
    """
    try:
        async with httpx.AsyncClient() as client:
            # Build JSON body with only provided fields
            data = {}
            if title is not None and title.strip():
                data["title"] = title.strip()
            if status is not None and status.strip():
                data["status"] = status.strip()
            if description is not None:
                # Send empty string as None for backend validation
                data["description"] = description.strip() if description.strip() else None

            if not data:
                return None, "No fields to update"

            response = await client.patch(
                f"{API_BASE}/documents/{document_id}",
                json=data  # Send as JSON body, not query params
            )
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
        return None, f"Error updating document: {str(e)}"

async def archive_document(document_id: str):
    """Archive a document"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.patch(f"{API_BASE}/documents/{document_id}/archive")
            response.raise_for_status()
            return response.json(), None
    except httpx.HTTPStatusError as e:
        return None, f"Error: {e.response.text}"
    except Exception as e:
        return None, f"Error archiving document: {str(e)}"

async def get_document_versions(document_id: str):
    """Fetch all versions for a document"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{API_BASE}/documents/{document_id}/versions")
            response.raise_for_status()
            return response.json()
    except Exception as e:
        print(f"Error fetching document versions: {e}")
        return []

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

def render_documents_list(documents, users=None, status_filter=None, error=None, success=None):
    """Render the documents list view"""
    return documents_page_layout(
        Div(
            Div(
                H1("Documents"),
                Div(
                    A("Back to Home", href="/", cls="btn btn-secondary"),
                    A("Create New Document", href="/documents/create", cls="btn"),
                ),
                cls="header"
            ),

            Div(
                error and Div(error, cls="error") or None,
                success and Div(success, cls="success") or None,

                # Filter bar
                Div(
                    Form(
                        Label("Filter by Status:", style="margin-right: 10px;"),
                        Select(
                            Option("All Documents", value="", selected=(not status_filter)),
                            Option("Draft", value="Draft", selected=(status_filter == "Draft")),
                            Option("Review", value="Review", selected=(status_filter == "Review")),
                            Option("Approved", value="Approved", selected=(status_filter == "Approved")),
                            Option("Archived", value="Archived", selected=(status_filter == "Archived")),
                            name="status",
                            onchange="this.form.submit()"
                        ),
                        method="GET",
                        action="/documents"
                    ),
                    cls="filter-bar"
                ),

                H2(f"{status_filter or 'All'} Documents ({len(documents)})"),

                documents and Ul(
                    *[Li(
                        Div(
                            Div(
                                H3(doc.get("title")),
                                P(doc.get("description") or "No description", style="font-style: italic;"),
                                P(
                                    Span("Status: ", style="font-weight: bold;"),
                                    Span(
                                        doc.get("status"),
                                        cls=f"badge badge-{doc.get('status', '').lower()}"
                                    )
                                ),
                                P(f"Created: {doc.get('created_at', 'N/A')[:10]}"),
                                P(f"Updated: {doc.get('updated_at', 'N/A')[:10]}"),
                                cls="document-info"
                            ),
                            Div(
                                A("View Details", href=f"/documents/{doc['id']}", cls="btn"),
                                A("Edit", href=f"/documents/{doc['id']}/edit", cls="btn btn-secondary"),
                                doc.get("status") != "Archived" and Form(
                                    Button("Archive", type="submit", cls="btn btn-warning"),
                                    method="POST",
                                    action=f"/documents/{doc['id']}/archive"
                                ) or None,
                                cls="document-actions"
                            ),
                            cls="document-item"
                        )
                    ) for doc in documents],
                    cls="document-list"
                ) or Div(
                    P("No documents found."),
                    A("Create your first document", href="/documents/create", cls="btn"),
                    cls="empty-state"
                ),
                cls="content"
            )
        )
    )

def render_document_form(title, action, users, document=None, selected_user_id=None, error=None):
    """Render document creation/edit form"""
    return documents_page_layout(
        Div(
            Div(
                H1(title),
                A("Back to Documents", href="/documents", cls="btn btn-secondary"),
                cls="header"
            ),

            Div(
                error and Div(error, cls="error") or None,

                Form(
                    Div(
                        Label("Title (required)", _for="title"),
                        Input(
                            type="text",
                            name="title",
                            id="title",
                            value=document.get("title") if document else "",
                            required=True,
                            placeholder="Enter document title"
                        ),
                        cls="form-group"
                    ),

                    Div(
                        Label("Description", _for="description"),
                        Textarea(
                            document.get("description") if document else "",
                            name="description",
                            id="description",
                            placeholder="Enter document description (optional)"
                        ),
                        cls="form-group"
                    ),

                    # Only show created_by for new documents
                    not document and Div(
                        Label("Created By (required)", _for="created_by"),
                        Select(
                            Option("-- Select User --", value="", selected=not selected_user_id),
                            *[Option(
                                f"{user.get('full_name') or user.get('email')} ({user.get('email')})",
                                value=user.get("id"),
                                selected=(selected_user_id == user.get("id"))
                            ) for user in users],
                            name="created_by",
                            id="created_by",
                            required=True
                        ),
                        cls="form-group"
                    ) or None,

                    # Only show status for editing
                    document and Div(
                        Label("Status", _for="status"),
                        Select(
                            Option("Draft", value="Draft", selected=(document.get("status") == "Draft")),
                            Option("Review", value="Review", selected=(document.get("status") == "Review")),
                            Option("Approved", value="Approved", selected=(document.get("status") == "Approved")),
                            Option("Archived", value="Archived", selected=(document.get("status") == "Archived")),
                            name="status",
                            id="status"
                        ),
                        cls="form-group"
                    ) or None,

                    Div(
                        Button("Cancel", type="button", onclick="window.location.href='/documents'", cls="btn btn-secondary"),
                        Button("Save Document", type="submit", cls="btn"),
                        style="display: flex; gap: 10px; justify-content: flex-end;"
                    ),

                    method="POST",
                    action=action
                ),
                cls="content"
            )
        )
    )

def render_document_details(document, versions=None, error=None, success=None):
    """Render document details view"""
    if not document:
        return documents_page_layout(
            Div(
                Div(
                    H1("Document Not Found"),
                    A("Back to Documents", href="/documents", cls="btn btn-secondary"),
                    cls="header"
                ),
                Div(
                    P("The requested document could not be found."),
                    cls="content"
                )
            )
        )

    creator = document.get("creator", {})
    current_version_id = document.get("current_version_id")

    return documents_page_layout(
        Div(
            Div(
                H1(document.get("title")),
                Div(
                    A("Back to Documents", href="/documents", cls="btn btn-secondary"),
                    A("Edit Document", href=f"/documents/{document['id']}/edit", cls="btn"),
                    A("Upload New Version", href=f"/upload?mode=existing&document_id={document['id']}", cls="btn btn-success"),
                    document.get("status") != "Archived" and Form(
                        Button("Archive Document", type="submit", cls="btn btn-warning"),
                        method="POST",
                        action=f"/documents/{document['id']}/archive",
                        style="display: inline;"
                    ) or None,
                ),
                cls="header"
            ),

            Div(
                error and Div(error, cls="error") or None,
                success and Div(success, cls="success") or None,

                # Document Information
                Div(
                    H3("Document Information"),
                    Div(
                        Div(Span("ID:", cls="detail-label"), Span(document.get("id"), cls="detail-value"), cls="detail-row"),
                        Div(Span("Title:", cls="detail-label"), Span(document.get("title"), cls="detail-value"), cls="detail-row"),
                        Div(
                            Span("Status:", cls="detail-label"),
                            Span(
                                Span(
                                    document.get("status"),
                                    cls=f"badge badge-{document.get('status', '').lower()}"
                                ),
                                cls="detail-value"
                            ),
                            cls="detail-row"
                        ),
                        Div(Span("Description:", cls="detail-label"), Span(document.get("description") or "N/A", cls="detail-value"), cls="detail-row"),
                        Div(Span("Created By:", cls="detail-label"), Span(creator.get("email") or "N/A", cls="detail-value"), cls="detail-row"),
                        Div(Span("Created At:", cls="detail-label"), Span(document.get("created_at"), cls="detail-value"), cls="detail-row"),
                        Div(Span("Updated At:", cls="detail-label"), Span(document.get("updated_at"), cls="detail-value"), cls="detail-row"),
                    ),
                    cls="detail-section"
                ),

                # Document Versions
                Div(
                    H3(f"Versions ({len(versions) if versions else 0})"),
                    versions and len(versions) > 0 and Ul(
                        *[Li(
                            Div(
                                H4(
                                    f"Version {version.get('version_number')}",
                                    (version.get('id') == current_version_id) and Span(" (Current)", style="color: #007bff; font-weight: bold;") or None
                                ),
                                P(f"Created: {version.get('created_at')}"),
                                version.get('change_summary') and P(f"Changes: {version.get('change_summary')}") or None,
                                version.get('pdf_url') and P(
                                    A("Download PDF", href=version.get('pdf_url'), target="_blank", cls="btn btn-secondary")
                                ) or None,
                                version.get('markdown_content') and Div(
                                    P(Strong("Content Preview:")),
                                    Div(
                                        version.get('markdown_content')[:500] + ("..." if len(version.get('markdown_content', '')) > 500 else ""),
                                        cls="markdown-content"
                                    )
                                ) or None,
                                cls=f"version-item {'version-current' if version.get('id') == current_version_id else ''}"
                            )
                        ) for version in versions]
                    ) or P("No versions yet.", style="color: #666;"),
                    cls="detail-section"
                ),

                # Document Permissions
                Div(
                    H3(
                        "Permissions",
                        A("Manage Permissions", href=f"/permissions/document/{document['id']}", cls="btn", style="margin-left: 20px; font-size: 14px;")
                    ),
                    document.get("permissions") and len(document.get("permissions")) > 0 and Ul(
                        *[Li(
                            Div(
                                Span(f"User ID: {perm.get('user_id')}"),
                                Span(perm.get('permission_type'), cls="badge", style="margin-left: 10px;"),
                            ),
                            cls="permission-item"
                        ) for perm in document.get("permissions", [])]
                    ) or P("No permissions granted yet.", style="color: #666;"),
                    cls="detail-section"
                ),

                cls="content"
            )
        )
    )
