from fasthtml.common import *
from frontend.lib.api import http_client
from frontend.components.navbar import navbar
from datetime import datetime


def register(rt):
    @rt('/documents')
    def get():
        # Load documents and users (for create form)
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

        return Div(
            navbar('documents'),
            Titled('Documents',
                Card(
                    H3('Create Document'),
                    Form(
                        Div(Label('Title:', For='title'), Input(type='text', id='title', name='title', required=True)),
                        Div(Label('Description:', For='description'), Textarea(id='description', name='description')),
                        Div(Label('Created By:', For='created_by'),
                            Select(
                                *[Option(u.get('full_name') or u['email'], value=u['id']) for u in users],
                                id='created_by', name='created_by', required=True
                            )
                        ),
                        Button('Create', type='submit'),
                        hx_post='/documents/create',
                        hx_target='#documents-list',
                        hx_swap='outerHTML'
                    )
                ),
                Div(
                    H3('Existing Documents'),
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
                return Div(*[document_card(d) for d in documents], id='documents-list')
            else:
                detail = resp.json().get('detail', 'Unknown error')
                return Div(P(f'✗ Error: {detail}', style='color: red;'), id='documents-list')
        except Exception as e:
            return Div(P(f'✗ Error connecting to API: {str(e)}', style='color: red;'), id='documents-list')

    @rt('/documents/{doc_id}/archive')
    def patch(doc_id: str):
        try:
            resp = http_client.patch(f'/documents/{doc_id}/archive')
            if resp.status_code == 200:
                # Replace the card with the updated one
                return document_card(resp.json())
            else:
                return P('Failed to archive', style='color: red;')
        except Exception as e:
            return P(f'Error: {str(e)}', style='color: red;')

    @rt('/documents/{doc_id}')
    def get(doc_id: str):
        try:
            resp = http_client.get(f'/documents/{doc_id}')
            if resp.status_code != 200:
                return Titled('Document', P('Not found'))
            doc = resp.json()
            return Titled(doc['title'],
                Card(
                    P(Strong('Status: '), doc.get('status', 'Unknown')),
                    P(Strong('Description: '), doc.get('description') or '—'),
                    P(Strong('Created: '), _fmt_dt(doc.get('created_at'))),
                ),
                Card(
                    H3('Versions'),
                    versions_list(doc_id)
                ),
                Div(A('← Back to Documents', href='/documents'), style='margin-top: 2rem;')
            )
        except Exception as e:
            return Titled('Document', P(f'Error: {str(e)}'))


def versions_list(doc_id: str):
    try:
        vresp = http_client.get(f'/documents/{doc_id}/versions')
        versions = vresp.json() if vresp.status_code == 200 else []
        if not versions:
            return P('No versions yet.')
        return Div(
            *[
                Card(
                    P(Strong('Version: '), v.get('version_number')),
                    P(Strong('Created: '), _fmt_dt(v.get('created_at'))),
                ) for v in versions
            ]
        )
    except Exception:
        return P('Failed to load versions')


def document_card(doc: dict):
    return Card(
        Div(
            H4(doc['title']),
            P(Strong('Status: '), doc.get('status', 'Unknown')),
            P(Strong('Created: '), _fmt_dt(doc.get('created_at'))),
            Div(
                Button('View', onclick=f"window.location='/documents/{doc['id']}'"),
                Button('Archive', hx_patch=f"/documents/{doc['id']}/archive", hx_target=f"#doc-{doc['id']}", hx_swap='outerHTML'),
                style='display: flex; gap: 0.5rem;'
            ),
            id=f"doc-{doc['id']}",
            style='border-left: 3px solid #444; padding: 1rem;'
        )
    )


def _fmt_dt(val: str | None):
    if not val:
        return '—'
    try:
        return datetime.fromisoformat(val.replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M')
    except Exception:
        return '—'
