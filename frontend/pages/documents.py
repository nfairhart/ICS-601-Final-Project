from fasthtml.common import *
import httpx
from typing import Optional

API_BASE = "http://localhost:8000"

def documents_page_layout(content):
    """Common layout for documents pages"""
    return Html(
        Head(
            Title("Documents - Document Control System"),
            Style("""
                body {
                    font-family: Arial, sans-serif;
                    max-width: 1400px;
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
                    margin-right: 10px;
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
                .btn-warning {
                    background: #ffc107;
                    color: #212529;
                }
                .btn-warning:hover {
                    background: #e0a800;
                }
                .btn-success {
                    background: #28a745;
                }
                .btn-success:hover {
                    background: #218838;
                }
                .content {
                    background: white;
                    padding: 30px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }
                .document-list {
                    list-style: none;
                    padding: 0;
                }
                .document-item {
                    padding: 20px;
                    border-bottom: 1px solid #e9ecef;
                    display: flex;
                    justify-content: space-between;
                    align-items: flex-start;
                    transition: background 0.2s;
                }
                .document-item:hover {
                    background: #f8f9fa;
                }
                .document-item:last-child {
                    border-bottom: none;
                }
                .document-info {
                    flex-grow: 1;
                }
                .document-info h3 {
                    margin: 0 0 10px 0;
                    color: #333;
                }
                .document-info p {
                    margin: 5px 0;
                    color: #666;
                    font-size: 14px;
                }
                .document-actions {
                    display: flex;
                    gap: 10px;
                    flex-wrap: wrap;
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
                .form-group input, .form-group textarea, .form-group select {
                    width: 100%;
                    padding: 10px;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    font-size: 14px;
                    box-sizing: border-box;
                    font-family: Arial, sans-serif;
                }
                .form-group textarea {
                    min-height: 100px;
                    resize: vertical;
                }
                .form-group input:focus, .form-group textarea:focus, .form-group select:focus {
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
                .document-details {
                    margin-top: 20px;
                }
                .detail-section {
                    margin-bottom: 30px;
                    padding: 20px;
                    background: #f8f9fa;
                    border-radius: 8px;
                }
                .detail-section h3 {
                    color: #333;
                    border-bottom: 2px solid #007bff;
                    padding-bottom: 10px;
                    margin-top: 0;
                }
                .detail-row {
                    display: flex;
                    padding: 10px 0;
                    border-bottom: 1px solid #e9ecef;
                }
                .detail-label {
                    font-weight: bold;
                    width: 200px;
                    color: #555;
                }
                .detail-value {
                    color: #333;
                    flex-grow: 1;
                }
                .badge {
                    display: inline-block;
                    padding: 4px 12px;
                    background: #007bff;
                    color: white;
                    border-radius: 12px;
                    font-size: 12px;
                    font-weight: bold;
                }
                .badge-draft {
                    background: #ffc107;
                    color: #212529;
                }
                .badge-archived {
                    background: #6c757d;
                }
                .filter-bar {
                    margin-bottom: 20px;
                    padding: 15px;
                    background: #f8f9fa;
                    border-radius: 4px;
                    display: flex;
                    gap: 10px;
                    align-items: center;
                }
                .version-list {
                    list-style: none;
                    padding: 0;
                }
                .version-item {
                    padding: 15px;
                    border: 1px solid #e9ecef;
                    border-radius: 4px;
                    margin-bottom: 10px;
                    background: white;
                }
                .version-item h4 {
                    margin: 0 0 10px 0;
                    color: #333;
                }
                .version-current {
                    border-color: #007bff;
                    background: #e7f3ff;
                }
                .markdown-content {
                    background: #f8f9fa;
                    padding: 15px;
                    border-radius: 4px;
                    border-left: 3px solid #007bff;
                    max-height: 300px;
                    overflow-y: auto;
                    font-family: monospace;
                    font-size: 12px;
                    white-space: pre-wrap;
                    word-wrap: break-word;
                }
                .permission-list {
                    list-style: none;
                    padding: 0;
                }
                .permission-item {
                    padding: 10px;
                    border-bottom: 1px solid #e9ecef;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                }
            """)
        ),
        Body(content)
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
    """Update a document"""
    try:
        async with httpx.AsyncClient() as client:
            params = {}
            if title:
                params["title"] = title
            if status:
                params["status"] = status
            if description:
                params["description"] = description

            response = await client.patch(f"{API_BASE}/documents/{document_id}", params=params)
            response.raise_for_status()
            return response.json(), None
    except httpx.HTTPStatusError as e:
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
