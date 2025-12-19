from fasthtml.common import *
import httpx
from pages.users import (
    get_users, get_user_by_id, get_user_documents, get_user_permissions,
    create_user, update_user,
    render_users_list, render_user_form, render_user_details
)
from pages.agent import (
    get_users_for_select as get_users_for_agent, query_agent,
    render_agent_page, render_agent_response
)
from pages.search import (
    get_users_for_select as get_users_for_search, search_documents,
    render_search_page
)
from pages.upload import (
    get_users_for_select as get_users_for_upload,
    get_documents_for_select,
    upload_pdf_to_document,
    create_document_from_pdf,
    render_upload_page
)
from pages.permissions import (
    get_documents as get_documents_for_permissions,
    get_document_by_id as get_document_for_permissions,
    get_users as get_users_for_permissions,
    get_document_permissions,
    grant_permission,
    revoke_permission,
    render_permissions_main,
    render_grant_permission_form,
    render_document_permissions
)
from pages.documents import (
    get_documents,
    get_document_by_id,
    create_document,
    update_document,
    archive_document,
    get_document_versions,
    get_users as get_users_for_documents,
    render_documents_list,
    render_document_form,
    render_document_details
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
        ),
        Body(
            Div(
                H1("Document Control System"),
                P("Manage documents with version control, permissions, and AI-powered search")
            ),

            # First Row
            Div(
                Div(
                    H2("Documents"),
                    P("Create, view, and manage documents with version control."),
                    A("View Documents", href="/documents")
                ),
                Div(
                    H2("Upload PDF"),
                    P("Upload PDF files to create new documents or add versions."),
                    A("Upload PDF", href="/upload")
                ),
                Div(
                    H2("Search"),
                    P("Search through document content using RAG technology."),
                    A("Search Documents", href="/search")
                ),
                Div(
                    H2("AI Agent"),
                    P("Ask questions about your documents with AI assistance."),
                    A("Query AI Agent", href="/agent")
                )
            ),

            # Second Row
            Div(
                Div(
                    H2("Users"),
                    P("Manage users and view their documents and permissions."),
                    A("Manage Users", href="/users")
                ),
                Div(
                    H2("Permissions"),
                    P("Control document access by granting permissions to users."),
                    A("Manage Permissions", href="/permissions")
                )
            )
        )
    )

@rt("/documents")
async def get(status: str = ""):
    """Documents listing page"""
    documents = await get_documents(status if status else None)
    users = await get_users_for_documents()
    return render_documents_list(
        documents=documents,
        users=users,
        status_filter=status if status else None
    )

@rt("/documents/create")
async def get():
    """Create document form"""
    users = await get_users_for_documents()
    return render_document_form("Create New Document", "/documents/create", users=users)

@rt("/documents/create")
async def post(title: str, created_by: str, description: str = ""):
    """Handle document creation"""
    users = await get_users_for_documents()

    document, error = await create_document(
        title=title,
        created_by=created_by,
        description=description if description else None
    )

    if error:
        return render_document_form(
            "Create New Document",
            "/documents/create",
            users=users,
            selected_user_id=created_by,
            error=error
        )

    # Redirect to document details
    doc_details = await get_document_by_id(document["id"])
    versions = await get_document_versions(document["id"])
    return render_document_details(
        document=doc_details,
        versions=versions,
        success="Document created successfully!"
    )

@rt("/documents/{document_id}")
async def get(document_id: str):
    """Document details page"""
    document = await get_document_by_id(document_id)
    versions = await get_document_versions(document_id)
    return render_document_details(document=document, versions=versions)

@rt("/documents/{document_id}/edit")
async def get(document_id: str):
    """Edit document form"""
    document = await get_document_by_id(document_id)
    users = await get_users_for_documents()

    if not document:
        documents = await get_documents()
        return render_documents_list(documents=documents, error="Document not found")

    return render_document_form(
        "Edit Document",
        f"/documents/{document_id}/edit",
        users=users,
        document=document
    )

@rt("/documents/{document_id}/edit")
async def post(document_id: str, title: str = "", status: str = "", description: str = ""):
    """Handle document update"""
    users = await get_users_for_documents()

    document, error = await update_document(
        document_id=document_id,
        title=title if title else None,
        status=status if status else None,
        description=description if description else None
    )

    if error:
        existing_doc = await get_document_by_id(document_id)
        return render_document_form(
            "Edit Document",
            f"/documents/{document_id}/edit",
            users=users,
            document=existing_doc,
            error=error
        )

    # Redirect to document details
    updated_doc = await get_document_by_id(document_id)
    versions = await get_document_versions(document_id)
    return render_document_details(
        document=updated_doc,
        versions=versions,
        success="Document updated successfully!"
    )

@rt("/documents/{document_id}/archive")
async def post(document_id: str):
    """Handle document archival"""
    result, error = await archive_document(document_id)

    # Redirect to document details
    document = await get_document_by_id(document_id)
    versions = await get_document_versions(document_id)

    if error:
        return render_document_details(
            document=document,
            versions=versions,
            error=error
        )

    return render_document_details(
        document=document,
        versions=versions,
        success="Document archived successfully!"
    )

@rt("/upload")
async def get(mode: str = "new"):
    """PDF upload page"""
    users = await get_users_for_upload()
    documents = await get_documents_for_select()
    return render_upload_page(users=users, documents=documents, mode=mode)

@rt("/upload/new")
async def post(pdf_file: UploadFile, created_by: str, title: str = "", description: str = ""):
    """Handle new document creation from PDF"""
    users = await get_users_for_upload()
    documents = await get_documents_for_select()

    # Create document from PDF
    result, error = await create_document_from_pdf(
        pdf_file=pdf_file,
        created_by=created_by,
        title=title if title else None,
        description=description if description else None
    )

    if error:
        return render_upload_page(
            users=users,
            documents=documents,
            mode="new",
            selected_user_id=created_by,
            error=error
        )

    return render_upload_page(
        users=users,
        documents=documents,
        mode="new",
        success=result.get("message", "Document created successfully!"),
        result=result
    )

@rt("/upload/existing")
async def post(pdf_file: UploadFile, document_id: str, created_by: str, change_summary: str = ""):
    """Handle PDF upload to existing document"""
    users = await get_users_for_upload()
    documents = await get_documents_for_select()

    # Upload PDF to document
    result, error = await upload_pdf_to_document(
        document_id=document_id,
        pdf_file=pdf_file,
        created_by=created_by,
        change_summary=change_summary if change_summary else None
    )

    if error:
        return render_upload_page(
            users=users,
            documents=documents,
            mode="existing",
            selected_user_id=created_by,
            selected_document_id=document_id,
            error=error
        )

    return render_upload_page(
        users=users,
        documents=documents,
        mode="existing",
        success=result.get("message", "PDF uploaded successfully!"),
        result=result
    )

@rt("/search")
async def get():
    """Search page"""
    users = await get_users_for_search()
    return render_search_page(users)

@rt("/search")
async def post(query: str, user_id: str, top_k: int = 5):
    """Handle search query"""
    users = await get_users_for_search()

    # Perform search
    results, error = await search_documents(query, user_id, top_k)

    if error:
        return render_search_page(
            users=users,
            selected_user_id=user_id,
            search_query=query,
            top_k=top_k,
            error=error
        )

    return render_search_page(
        users=users,
        selected_user_id=user_id,
        search_query=query,
        top_k=top_k,
        search_results=results
    )

@rt("/agent")
async def get(user_id: str = ""):
    """AI Agent query page"""
    users = await get_users_for_agent()
    return render_agent_page(users, selected_user_id=user_id if user_id else None)

@rt("/agent/query")
async def post(query: str, user_id: str):
    """Handle AI agent query"""
    users = await get_users_for_agent()

    # Initialize chat history with user's query
    chat_history = [
        {"role": "user", "content": query}
    ]

    # Query the agent
    response, error = await query_agent(query, user_id)

    if error:
        return render_agent_response(
            users=users,
            user_id=user_id,
            chat_history=chat_history,
            error=error
        )

    # Add agent's response to chat history
    chat_history.append({
        "role": "agent",
        "content": response.get("response", "No response received")
    })

    return render_agent_response(
        users=users,
        user_id=user_id,
        chat_history=chat_history
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
    documents = await get_user_documents(user_id)
    permissions = await get_user_permissions(user_id)

    # Add documents and permissions to user object
    if user:
        user['documents'] = documents
        user['permissions'] = permissions

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
async def get(mode: str = "grant"):
    """Permissions management page"""
    documents = await get_documents_for_permissions()
    return render_permissions_main(documents=documents, mode=mode)

@rt("/permissions/grant")
async def get(document_id: str = ""):
    """Grant permission form"""
    if not document_id:
        documents = await get_documents_for_permissions()
        return render_permissions_main(documents=documents, mode="grant", error="Please select a document")

    document = await get_document_for_permissions(document_id)
    users = await get_users_for_permissions()
    return render_grant_permission_form(document=document, users=users)

@rt("/permissions/grant")
async def post(document_id: str, user_id: str, permission_type: str):
    """Handle permission grant"""
    # Grant the permission
    result, error = await grant_permission(document_id, user_id, permission_type)

    if error:
        document = await get_document_for_permissions(document_id)
        users = await get_users_for_permissions()
        return render_grant_permission_form(
            document=document,
            users=users,
            selected_user_id=user_id,
            error=error
        )

    # Redirect to document permissions view
    document = await get_document_for_permissions(document_id)
    permissions = await get_document_permissions(document_id)
    users = await get_users_for_permissions()
    users_map = {user["id"]: user for user in users}

    return render_document_permissions(
        document=document,
        permissions=permissions,
        users_map=users_map,
        success="Permission granted successfully!"
    )

@rt("/permissions/document/{document_id}")
async def get(document_id: str):
    """View permissions for a specific document"""
    document = await get_document_for_permissions(document_id)
    permissions = await get_document_permissions(document_id)
    users = await get_users_for_permissions()
    users_map = {user["id"]: user for user in users}

    return render_document_permissions(
        document=document,
        permissions=permissions,
        users_map=users_map
    )

@rt("/permissions/revoke")
async def post(permission_id: str, document_id: str):
    """Handle permission revocation"""
    result, error = await revoke_permission(permission_id)

    # Redirect back to document permissions view
    document = await get_document_for_permissions(document_id)
    permissions = await get_document_permissions(document_id)
    users = await get_users_for_permissions()
    users_map = {user["id"]: user for user in users}

    if error:
        return render_document_permissions(
            document=document,
            permissions=permissions,
            users_map=users_map,
            error=error
        )

    return render_document_permissions(
        document=document,
        permissions=permissions,
        users_map=users_map,
        success="Permission revoked successfully!"
    )

# Run the app
serve()
