from fasthtml.common import *
import httpx
from typing import Optional, List, Dict

API_BASE = "http://localhost:8000"

def upload_page_layout(content):
    """Common layout for upload pages"""
    return Html(
        Head(
            Title("Upload PDF - Document Control System"),
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
                .upload-options {
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 20px;
                    margin-bottom: 30px;
                }
                .upload-card {
                    border: 2px solid #e9ecef;
                    border-radius: 8px;
                    padding: 20px;
                    background: #f8f9fa;
                    transition: all 0.2s;
                }
                .upload-card:hover {
                    border-color: #007bff;
                    background: white;
                }
                .upload-card h3 {
                    margin-top: 0;
                    color: #333;
                }
                .upload-card p {
                    color: #6c757d;
                    line-height: 1.6;
                }
                .form-section {
                    background: white;
                    border: 1px solid #dee2e6;
                    border-radius: 8px;
                    padding: 25px;
                    margin-bottom: 20px;
                }
                .form-section h3 {
                    margin-top: 0;
                    margin-bottom: 20px;
                    color: #333;
                    border-bottom: 2px solid #007bff;
                    padding-bottom: 10px;
                }
                .form-group {
                    margin-bottom: 20px;
                }
                .form-label {
                    display: block;
                    font-weight: bold;
                    margin-bottom: 8px;
                    color: #333;
                }
                .form-input,
                .form-select,
                .form-textarea {
                    width: 100%;
                    padding: 12px;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    font-size: 14px;
                    font-family: Arial, sans-serif;
                    box-sizing: border-box;
                }
                .form-input:focus,
                .form-select:focus,
                .form-textarea:focus {
                    outline: none;
                    border-color: #007bff;
                    box-shadow: 0 0 0 3px rgba(0,123,255,0.1);
                }
                .form-textarea {
                    resize: vertical;
                    min-height: 80px;
                }
                .file-input-wrapper {
                    position: relative;
                    display: inline-block;
                    width: 100%;
                }
                .file-input {
                    width: 100%;
                    padding: 12px;
                    border: 2px dashed #007bff;
                    border-radius: 4px;
                    background: #f8f9fa;
                    cursor: pointer;
                    font-size: 14px;
                }
                .file-input:hover {
                    background: #e9ecef;
                }
                .file-input::file-selector-button {
                    padding: 8px 16px;
                    background: #007bff;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    cursor: pointer;
                    margin-right: 10px;
                }
                .file-input::file-selector-button:hover {
                    background: #0056b3;
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
                .warning-box {
                    background: #fff3cd;
                    border-left: 4px solid #ffc107;
                    padding: 15px;
                    margin-bottom: 20px;
                    border-radius: 4px;
                }
                .warning-box p {
                    margin: 5px 0;
                    color: #856404;
                }
                .success {
                    color: #155724;
                    padding: 15px;
                    background: #d4edda;
                    border: 1px solid #c3e6cb;
                    border-radius: 4px;
                    margin-bottom: 20px;
                }
                .error {
                    color: #dc3545;
                    padding: 15px;
                    background: #f8d7da;
                    border: 1px solid #f5c6cb;
                    border-radius: 4px;
                    margin-bottom: 20px;
                }
                .form-help {
                    font-size: 13px;
                    color: #6c757d;
                    margin-top: 5px;
                }
                .required {
                    color: #dc3545;
                }
                .button-group {
                    display: flex;
                    gap: 10px;
                    margin-top: 20px;
                }
                .tabs {
                    display: flex;
                    gap: 10px;
                    margin-bottom: 20px;
                    border-bottom: 2px solid #dee2e6;
                }
                .tab {
                    padding: 12px 24px;
                    background: transparent;
                    border: none;
                    border-bottom: 3px solid transparent;
                    cursor: pointer;
                    font-size: 15px;
                    font-weight: 500;
                    color: #6c757d;
                    text-decoration: none;
                    transition: all 0.2s;
                }
                .tab:hover {
                    color: #007bff;
                }
                .tab.active {
                    color: #007bff;
                    border-bottom-color: #007bff;
                }
                .hidden {
                    display: none;
                }
                .version-info {
                    background: #f8f9fa;
                    padding: 15px;
                    border-radius: 4px;
                    margin-top: 20px;
                }
                .version-info h4 {
                    margin-top: 0;
                    color: #333;
                }
                .version-detail {
                    display: flex;
                    justify-content: space-between;
                    padding: 8px 0;
                    border-bottom: 1px solid #dee2e6;
                }
                .version-detail:last-child {
                    border-bottom: none;
                }
                .version-label {
                    font-weight: bold;
                    color: #6c757d;
                }
                .version-value {
                    color: #333;
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

async def get_documents_for_select():
    """Fetch all documents for dropdown selection"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{API_BASE}/documents")
            response.raise_for_status()
            return response.json()
    except Exception as e:
        print(f"Error fetching documents: {e}")
        return []

async def upload_pdf_to_document(document_id: str, pdf_file, created_by: str, change_summary: Optional[str] = None):
    """Upload PDF to existing document"""
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            files = {"pdf_file": (pdf_file.filename, pdf_file.file, pdf_file.content_type)}
            data = {
                "created_by": created_by,
            }
            if change_summary:
                data["change_summary"] = change_summary

            response = await client.post(
                f"{API_BASE}/documents/{document_id}/upload-pdf",
                files=files,
                data=data
            )
            response.raise_for_status()
            return response.json(), None
    except httpx.HTTPStatusError as e:
        try:
            error_detail = e.response.json().get("detail", str(e))
        except:
            error_detail = str(e)
        return None, f"Error: {error_detail}"
    except httpx.TimeoutException:
        return None, "Upload timed out. Please try a smaller file or try again."
    except Exception as e:
        return None, f"Error uploading PDF: {str(e)}"

async def create_document_from_pdf(pdf_file, created_by: str, title: Optional[str] = None, description: Optional[str] = None):
    """Create new document from PDF upload"""
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            files = {"pdf_file": (pdf_file.filename, pdf_file.file, pdf_file.content_type)}
            data = {
                "created_by": created_by,
            }
            if title:
                data["title"] = title
            if description:
                data["description"] = description

            response = await client.post(
                f"{API_BASE}/documents/create-from-pdf",
                files=files,
                data=data
            )
            response.raise_for_status()
            return response.json(), None
    except httpx.HTTPStatusError as e:
        try:
            error_detail = e.response.json().get("detail", str(e))
        except:
            error_detail = str(e)
        return None, f"Error: {error_detail}"
    except httpx.TimeoutException:
        return None, "Upload timed out. Please try a smaller file or try again."
    except Exception as e:
        return None, f"Error creating document from PDF: {str(e)}"

def render_upload_page(
    users: List[Dict],
    documents: List[Dict],
    mode: str = "new",
    selected_user_id: Optional[str] = None,
    selected_document_id: Optional[str] = None,
    success: Optional[str] = None,
    error: Optional[str] = None,
    result: Optional[Dict] = None
):
    """Render the upload page with two modes: new document or existing document"""

    return upload_page_layout(
        Div(
            Div(
                H1("Upload PDF"),
                A("Back to Home", href="/", cls="btn btn-secondary"),
                cls="header"
            ),

            Div(
                success and Div(success, cls="success") or None,
                error and Div(error, cls="error") or None,

                Div(
                    P(Strong("Upload PDF files"), " to create new documents or add new versions to existing documents."),
                    P("PDFs are automatically converted to markdown and indexed for search."),
                    cls="info-box"
                ),

                # Tab navigation
                Div(
                    A("Create New Document",
                      href="/upload?mode=new",
                      cls=f"tab {'active' if mode == 'new' else ''}"),
                    A("Add to Existing Document",
                      href="/upload?mode=existing",
                      cls=f"tab {'active' if mode == 'existing' else ''}"),
                    cls="tabs"
                ),

                # New Document Form
                mode == "new" and Div(
                    Form(
                        Div(
                            H3("Create New Document from PDF"),

                            Div(
                                P(Strong("What happens when you upload:")),
                                Ul(
                                    Li("PDF is uploaded to Supabase storage"),
                                    Li("PDF is converted to markdown using MarkItDown"),
                                    Li("Document and first version are created"),
                                    Li("Content is indexed in RAG for AI search"),
                                ),
                                cls="info-box"
                            ),

                            Div(
                                Label("User ", Span("*", cls="required"), cls="form-label"),
                                Select(
                                    Option("Select a user...", value="", selected=not selected_user_id),
                                    *[Option(
                                        f"{user.get('full_name') or user.get('email')} ({user.get('email')})",
                                        value=user['id'],
                                        selected=(selected_user_id == user['id'])
                                    ) for user in users],
                                    name="created_by",
                                    cls="form-select",
                                    required=True
                                ),
                                P("Select the user who is creating this document", cls="form-help"),
                                cls="form-group"
                            ),

                            Div(
                                Label("PDF File ", Span("*", cls="required"), cls="form-label"),
                                Input(
                                    type="file",
                                    name="pdf_file",
                                    accept=".pdf",
                                    cls="file-input",
                                    required=True
                                ),
                                P("Select a PDF file to upload (will be converted to markdown)", cls="form-help"),
                                cls="form-group"
                            ),

                            Div(
                                Label("Document Title", cls="form-label"),
                                Input(
                                    type="text",
                                    name="title",
                                    placeholder="Leave blank to use filename",
                                    cls="form-input"
                                ),
                                P("Optional: Provide a custom title (defaults to filename)", cls="form-help"),
                                cls="form-group"
                            ),

                            Div(
                                Label("Description", cls="form-label"),
                                Textarea(
                                    name="description",
                                    placeholder="Optional description of the document",
                                    cls="form-textarea"
                                ),
                                P("Optional: Add a description for this document", cls="form-help"),
                                cls="form-group"
                            ),

                            Div(
                                Button("Create Document from PDF", type="submit", cls="btn btn-success"),
                                A("Cancel", href="/", cls="btn btn-secondary"),
                                cls="button-group"
                            ),

                            cls="form-section"
                        ),
                        method="POST",
                        action="/upload/new",
                        enctype="multipart/form-data"
                    )
                ) or None,

                # Existing Document Form
                mode == "existing" and Div(
                    Form(
                        Div(
                            H3("Add New Version to Existing Document"),

                            Div(
                                P(Strong("Note:"), " Adding a PDF creates a new version of the document."),
                                P("The version number will be automatically incremented."),
                                cls="warning-box"
                            ),

                            Div(
                                P(Strong("What happens when you upload:")),
                                Ul(
                                    Li("PDF is uploaded to Supabase storage"),
                                    Li("PDF is converted to markdown using MarkItDown"),
                                    Li("New version is created with incremented version number"),
                                    Li("New content is indexed in RAG (old version remains searchable)"),
                                    Li("Document's current version is updated to this version"),
                                ),
                                cls="info-box"
                            ),

                            Div(
                                Label("Document ", Span("*", cls="required"), cls="form-label"),
                                Select(
                                    Option("Select a document...", value="", selected=not selected_document_id),
                                    *[Option(
                                        f"{doc.get('title', 'Untitled')} (Status: {doc.get('status', 'Unknown')})",
                                        value=doc['id'],
                                        selected=(selected_document_id == doc['id'])
                                    ) for doc in documents],
                                    name="document_id",
                                    cls="form-select",
                                    required=True
                                ),
                                P("Select the document to add a new version to", cls="form-help"),
                                cls="form-group"
                            ),

                            Div(
                                Label("User ", Span("*", cls="required"), cls="form-label"),
                                Select(
                                    Option("Select a user...", value="", selected=not selected_user_id),
                                    *[Option(
                                        f"{user.get('full_name') or user.get('email')} ({user.get('email')})",
                                        value=user['id'],
                                        selected=(selected_user_id == user['id'])
                                    ) for user in users],
                                    name="created_by",
                                    cls="form-select",
                                    required=True
                                ),
                                P("Select the user who is uploading this version", cls="form-help"),
                                cls="form-group"
                            ),

                            Div(
                                Label("PDF File ", Span("*", cls="required"), cls="form-label"),
                                Input(
                                    type="file",
                                    name="pdf_file",
                                    accept=".pdf",
                                    cls="file-input",
                                    required=True
                                ),
                                P("Select a PDF file to upload as a new version", cls="form-help"),
                                cls="form-group"
                            ),

                            Div(
                                Label("Change Summary", cls="form-label"),
                                Textarea(
                                    name="change_summary",
                                    placeholder="Describe what changed in this version (optional)",
                                    cls="form-textarea"
                                ),
                                P("Optional: Describe the changes in this version", cls="form-help"),
                                cls="form-group"
                            ),

                            Div(
                                Button("Upload PDF Version", type="submit", cls="btn btn-success"),
                                A("Cancel", href="/", cls="btn btn-secondary"),
                                cls="button-group"
                            ),

                            cls="form-section"
                        ),
                        method="POST",
                        action="/upload/existing",
                        enctype="multipart/form-data"
                    )
                ) or None,

                # Success result display
                result and Div(
                    H4("Upload Successful!"),

                    # Processing info box
                    Div(
                        P(Strong("✓ PDF Processing Complete")),
                        P("Your PDF has been successfully processed with the following steps:"),
                        Ul(
                            Li("✓ PDF uploaded to Supabase storage"),
                            Li("✓ PDF converted to markdown using MarkItDown"),
                            Li("✓ Document version created in database"),
                            Li("✓ Content indexed in RAG (searchable via /search)"),
                        ),
                        cls="info-box"
                    ),

                    # Version details
                    Div(
                        H4("Version Details"),
                        Div(
                            Span("Document ID:", cls="version-label"),
                            Span(result.get('document', {}).get('id', 'N/A'), cls="version-value"),
                            cls="version-detail"
                        ),
                        result.get('document') and Div(
                            Span("Document Title:", cls="version-label"),
                            Span(result.get('document', {}).get('title', 'N/A'), cls="version-value"),
                            cls="version-detail"
                        ) or None,
                        Div(
                            Span("Version Number:", cls="version-label"),
                            Span(str(result.get('version', {}).get('version_number', 'N/A')), cls="version-value"),
                            cls="version-detail"
                        ),
                        result.get('version', {}).get('pdf_url') and Div(
                            Span("PDF URL:", cls="version-label"),
                            A("View PDF",
                              href=result.get('version', {}).get('pdf_url'),
                              target="_blank",
                              cls="version-value"),
                            cls="version-detail"
                        ) or None,
                        Div(
                            Span("Created At:", cls="version-label"),
                            Span(result.get('version', {}).get('created_at', 'N/A'), cls="version-value"),
                            cls="version-detail"
                        ),
                        cls="version-info"
                    ),

                    # Next steps
                    Div(
                        P(Strong("Next Steps:")),
                        Ul(
                            Li(A("Search for content", href="/search"), " - Find information in your uploaded document"),
                            Li(A("Ask AI Agent", href="/agent"), " - Query your documents using AI"),
                            Li(A("Upload another PDF", href="/upload"), " - Add more documents or versions"),
                        ),
                        cls="info-box"
                    ),

                    Div(
                        A("Upload Another PDF", href="/upload", cls="btn btn-success"),
                        A("Search Documents", href="/search", cls="btn"),
                        A("View Documents", href="/documents", cls="btn btn-secondary"),
                        cls="button-group"
                    )
                ) or None,

                cls="content"
            )
        )
    )
