from fasthtml.common import *
from frontend.lib.api import http_client
from frontend.components.navbar import navbar
from datetime import datetime


def register(rt):
    @rt('/documents')
    def get():
        # Load documents and users
        try:
            docs_resp = http_client.get('/documents')
            documents = docs_resp.json() if docs_resp.status_code == 200 else []
        except Exception:
            documents = []
        
        try:
            users_resp = http_client.get('/users')
            users = users_resp.json() if users_resp.status_code == 200 else []
        except Exception:
            users = []
        
        # Calculate stats
        total = len(documents)
        active = len([d for d in documents if d.get('status') == 'Active'])
        draft = len([d for d in documents if d.get('status') == 'Draft'])
        archived = len([d for d in documents if d.get('status') == 'Archived'])

        return Div(
            navbar('documents'),
            Titled('📄 Document Management',
                
                # Stats
                Div(
                    H3("Document Statistics"),
                    Div(
                        Div(
                            H2(str(total), style="margin: 0; color: #0066cc;"),
                            P("Total Documents", style="margin: 0.5rem 0 0 0; color: #666;")
                        ),
                        Div(
                            H2(str(active), style="margin: 0; color: #28a745;"),
                            P("Active", style="margin: 0.5rem 0 0 0; color: #666;")
                        ),
                        Div(
                            H2(str(draft), style="margin: 0; color: #ffc107;"),
                            P("Drafts", style="margin: 0.5rem 0 0 0; color: #666;")
                        ),
                        Div(
                            H2(str(archived), style="margin: 0; color: #6c757d;"),
                            P("Archived", style="margin: 0.5rem 0 0 0; color: #666;")
                        ),
                        cls="stats-grid"
                    ),
                    cls="card"
                ),
                
                # Create Document Form
                Div(
                    H3('➕ Create New Document'),
                    Form(
                        Div(
                            Label('Title:', For='title'),
                            Input(
                                type='text',
                                id='title',
                                name='title',
                                required=True,
                                placeholder='Q4 Sales Report'
                            ),
                            cls="form-row"
                        ),
                        Div(
                            Label('Description:', For='description'),
                            Textarea(
                                id='description',
                                name='description',
                                placeholder='Brief description of the document',
                                rows='3'
                            ),
                            cls="form-row"
                        ),
                        Div(
                            Label('Created By:', For='created_by'),
                            Select(
                                *[Option(
                                    f"{u.get('full_name', 'No Name')} ({u['email']})",
                                    value=u['id']
                                ) for u in users],
                                id='created_by',
                                name='created_by',
                                required=True
                            ) if users else P("⚠️ No users available. Create a user first."),
                            cls="form-row"
                        ),
                        Button('Create Document 🚀', type='submit') if users else None,
                        hx_post='/documents/create',
                        hx_target='#documents-list',
                        hx_swap='outerHTML'
                    ),
                    cls="card"
                ),
                
                # Documents List
                Div(
                    H3('📋 Existing Documents'),
                    Div(
                        *[document_card(d) for d in documents] if documents else P('No documents found.'),
                        id='documents-list'
                    )
                )
            )
        )

    @rt('/documents/create')
    async def post(title: str, description: str = None, created_by: str = None):
        try:
            resp = http_client.post('/documents', json={
                'title': title,
                'description': description,
                'created_by': created_by
            })
            
            if resp.status_code in (200, 201):
                docs_resp = http_client.get('/documents')
                documents = docs_resp.json() if docs_resp.status_code == 200 else []
                
                return Div(
                    Div(
                        P('✅ Document created successfully!', style='color: #28a745; font-weight: 600;'),
                        cls="card"
                    ),
                    *[document_card(d) for d in documents],
                    id='documents-list'
                )
            else:
                detail = resp.json().get('detail', 'Unknown error')
                return Div(
                    P(f'❌ Error: {detail}', style='color: #dc3545; font-weight: 600;'),
                    id='documents-list'
                )
        except Exception as e:
            return Div(
                P(f'❌ Error connecting to API: {str(e)}', style='color: #dc3545; font-weight: 600;'),
                id='documents-list'
            )

    @rt('/documents/{doc_id}/archive')
    def patch(doc_id: str):
        try:
            resp = http_client.patch(f'/documents/{doc_id}/archive')
            if resp.status_code == 200:
                return document_card(resp.json())
            else:
                return P('Failed to archive', style='color: #dc3545;')
        except Exception as e:
            return P(f'Error: {str(e)}', style='color: #dc3545;')

    @rt('/documents/{doc_id}')
    def get(doc_id: str):
        try:
            resp = http_client.get(f'/documents/{doc_id}')
            if resp.status_code != 200:
                return Titled('Document', P('Not found'))
            
            doc = resp.json()
            
            # Get versions
            vresp = http_client.get(f'/documents/{doc_id}/versions')
            versions = vresp.json() if vresp.status_code == 200 else []
            
            # Get permissions
            presp = http_client.get(f'/documents/{doc_id}/permissions')
            permissions = presp.json() if presp.status_code == 200 else []
            
            return Div(
                navbar('documents'),
                Titled(
                    f"📄 {doc['title']}",
                    
                    # Document Info
                    Div(
                        H3("Document Information"),
                        P(Strong('Status: '), Span(doc.get('status', 'Unknown'), cls=f"badge badge-{doc.get('status', '').lower()}")),
                        P(Strong('Description: '), doc.get('description') or '—'),
                        P(Strong('Created: '), _fmt_dt(doc.get('created_at'))),
                        P(Strong('Updated: '), _fmt_dt(doc.get('updated_at'))),
                        P(Strong('Document ID: '), Code(doc['id'])),
                        cls="card"
                    ),
                    
                    # Versions
                    Div(
                        H3(f"📚 Versions ({len(versions)})"),
                        Div(
                            *[
                                Div(
                                    P(Strong(f"Version {v.get('version_number')}")),
                                    P(Strong('Created: '), _fmt_dt(v.get('created_at'))),
                                    P(Strong('Change Summary: '), v.get('change_summary') or 'No summary'),
                                    style='padding: 1rem; background: #f8f9fa; border-left: 3px solid #0066cc; margin-bottom: 0.5rem;'
                                ) for v in versions
                            ] if versions else P('No versions yet.'),
                        ),
                        cls="card"
                    ),
                    
                    # Permissions
                    Div(
                        H3(f"🔐 Permissions ({len(permissions)})"),
                        Div(
                            *[
                                Div(
                                    P(Strong('User ID: '), perm.get('user_id')),
                                    P(Strong('Permission: '), perm.get('permission_type', 'read').upper()),
                                    P(Strong('Granted: '), _fmt_dt(perm.get('granted_at'))),
                                    style='padding: 1rem; background: #f8f9fa; border-left: 3px solid #28a745; margin-bottom: 0.5rem;'
                                ) for perm in permissions
                            ] if permissions else P('No permissions granted.'),
                        ),
                        cls="card"
                    ),
                    
                    # Actions
                    Div(
                        A('← Back to Documents', href='/documents', style='text-decoration: none; color: #0066cc; font-weight: 600;'),
                        style='margin-top: 2rem;'
                    )
                )
            )
        except Exception as e:
            return Titled('Document', P(f'Error: {str(e)}'))

    @rt('/documents/{doc_id}/add-version')
    def get(doc_id: str):
        # Get users for creator dropdown
        try:
            users_resp = http_client.get('/users')
            users = users_resp.json() if users_resp.status_code == 200 else []
        except Exception:
            users = []
        
        # Get current versions to determine next version number
        try:
            vresp = http_client.get(f'/documents/{doc_id}/versions')
            versions = vresp.json() if vresp.status_code == 200 else []
            next_version = max([v.get('version_number', 0) for v in versions], default=0) + 1
        except Exception:
            next_version = 1
        
        return Div(
            H3("➕ Add New Version"),
            Form(
                Div(
                    Label('Version Number:', For='version_number'),
                    Input(
                        type='number',
                        name='version_number',
                        id='version_number',
                        value=str(next_version),
                        required=True
                    ),
                    cls="form-row"
                ),
                Div(
                    Label('Markdown Content:', For='markdown_content'),
                    Textarea(
                        name='markdown_content',
                        id='markdown_content',
                        rows='10',
                        placeholder='# Document Content Write your document in markdown format...'
                    ),
                    cls="form-row"
                ),
                Div(
                    Label('Change Summary:', For='change_summary'),
                    Textarea(
                        name='change_summary',
                        id='change_summary',
                        rows='3',
                        placeholder='What changed in this version?'
                    ),
                    cls="form-row"
                ),
                Div(
                    Label('Created By:', For='created_by'),
                    Select(
                        *[Option(
                            f"{u.get('full_name', 'No Name')} ({u['email']})",
                            value=u['id']
                        ) for u in users],
                        name='created_by',
                        id='created_by'
                    ) if users else P("⚠️ No users available"),
                    cls="form-row"
                ),
                Div(
                    Button('Create Version 🚀', type='submit'),
                    Button('Cancel', onclick=f"window.location='/documents/{doc_id}'", type='button', style='background: #6c757d;'),
                    cls="btn-group"
                ),
                action=f'/documents/{doc_id}/create-version',
                method='POST'
            ),
            cls="card"
        )


def document_card(doc: dict):
    status = doc.get('status', 'Unknown')
    return Div(
        H4(doc['title'], style="margin-bottom: 0.5rem;"),
        P(
            Strong('Status: '),
            Span(status, cls=f"badge badge-{status.lower()}"),
            style="margin: 0.25rem 0;"
        ),
        P(Strong('Description: '), doc.get('description') or '—', style="margin: 0.25rem 0;"),
        P(Strong('Created: '), _fmt_dt(doc.get('created_at')), style="margin: 0.25rem 0;"),
        Div(
            Button('👁️ View', onclick=f"window.location='/documents/{doc['id']}'"),
            Button(
                '📦 Archive',
                hx_patch=f"/documents/{doc['id']}/archive",
                hx_target=f"#doc-{doc['id']}",
                hx_swap='outerHTML',
                style='background: #6c757d;'
            ) if status != 'Archived' else None,
            cls="btn-group"
        ),
        id=f"doc-{doc['id']}",
        cls="card",
        style='border-left: 4px solid #0066cc;'
    )


def _fmt_dt(val: str | None):
    if not val:
        return '—'
    try:
        return datetime.fromisoformat(val.replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M')
    except Exception:
        return '—'