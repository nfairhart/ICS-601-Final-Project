from fasthtml.common import *
from frontend.lib.api import http_client
from frontend.components.navbar import navbar
from datetime import datetime


def _safe_json(resp):
    try:
        return resp.json()
    except Exception:
        return None


def register(rt):
    @rt('/users')
    def get():
        try:
            resp = http_client.get('/users')
            data = _safe_json(resp) if resp.status_code == 200 else None
            users = data or []
        except Exception:
            users = []

        return Div(
            navbar("users"),
            Titled(
                "👥 User Management",
                
                # Stats
                Div(
                    H3("User Statistics"),
                    Div(
                        Div(
                            H2(str(len(users)), style="margin: 0; color: #9c27b0;"),
                            P("Total Users", style="margin: 0.5rem 0 0 0; color: #666;")
                        ),
                        Div(
                            H2(str(len([u for u in users if u.get('role') == 'admin'])), style="margin: 0; color: #dc3545;"),
                            P("Admins", style="margin: 0.5rem 0 0 0; color: #666;")
                        ),
                        Div(
                            H2(str(len([u for u in users if u.get('role') == 'user'])), style="margin: 0; color: #28a745;"),
                            P("Regular Users", style="margin: 0.5rem 0 0 0; color: #666;")
                        ),
                        cls="stats-grid"
                    ),
                    cls="card"
                ),
                
                # Create User Form
                Div(
                    H3("➕ Create New User"),
                    Form(
                        Div(
                            Label("Email:", For="email"),
                            Input(
                                type="email", 
                                name="email", 
                                id="email", 
                                required=True, 
                                placeholder="user@example.com"
                            ),
                            cls="form-row"
                        ),
                        Div(
                            Label("Full Name:", For="full_name"),
                            Input(
                                type="text", 
                                name="full_name", 
                                id="full_name", 
                                placeholder="John Doe"
                            ),
                            cls="form-row"
                        ),
                        Div(
                            Label("Role:", For="role"),
                            Select(
                                Option("User", value="user", selected=True),
                                Option("Admin", value="admin"),
                                Option("Manager", value="manager"),
                                name="role", 
                                id="role"
                            ),
                            cls="form-row"
                        ),
                        Button("Create User 🚀", type="submit"),
                        hx_post="/users/create",
                        hx_target="#users-list",
                        hx_swap="outerHTML"
                    ),
                    cls="card"
                ),
                
                # Users List
                Div(
                    H3("📋 Existing Users"),
                    Div(
                        *[user_card(u) for u in users] if users else P("No users found. Create one above!"),
                        id="users-list"
                    )
                )
            )
        )

    @rt('/users/create')
    async def post(email: str, full_name: str = None, role: str = 'user'):
        try:
            resp = http_client.post('/users', json={
                "email": email, 
                "full_name": full_name, 
                "role": role
            })
            
            if resp.status_code in (200, 201):
                users_resp = http_client.get('/users')
                users = _safe_json(users_resp) if users_resp.status_code == 200 else []
                
                return Div(
                    Div(
                        P("✅ User created successfully!", style="color: #28a745; font-weight: 600;"),
                        cls="card"
                    ),
                    *[user_card(u) for u in users],
                    id="users-list"
                )
            else:
                data = _safe_json(resp) or {}
                detail = data.get('detail') or (resp.text.strip() or 'Unknown error')
                return Div(
                    P(f"❌ Error: {detail}", style="color: #dc3545; font-weight: 600;"),
                    id="users-list"
                )
        except Exception as e:
            return Div(
                P(f"❌ Error connecting to API: {str(e)}", style="color: #dc3545; font-weight: 600;"),
                id="users-list"
            )

    @rt('/users/{user_id}/edit')
    def get(user_id: str):
        try:
            resp = http_client.get(f'/users/{user_id}')
            if resp.status_code != 200:
                return P('User not found')
            user = resp.json()
            
            return Div(
                H4('✏️ Edit User'),
                Form(
                    Input(type='hidden', name='user_id', value=user_id),
                    Div(
                        Label('Email:', For=f'email-{user_id}'),
                        Input(
                            type='email', 
                            name='email', 
                            id=f'email-{user_id}', 
                            value=user['email'], 
                            required=True
                        ),
                        cls="form-row"
                    ),
                    Div(
                        Label('Full Name:', For=f'full_name-{user_id}'),
                        Input(
                            type='text', 
                            name='full_name', 
                            id=f'full_name-{user_id}', 
                            value=user.get('full_name', '')
                        ),
                        cls="form-row"
                    ),
                    Div(
                        Label('Role:', For=f'role-{user_id}'),
                        Select(
                            Option('User', value='user', selected=user.get('role') == 'user'),
                            Option('Admin', value='admin', selected=user.get('role') == 'admin'),
                            Option('Manager', value='manager', selected=user.get('role') == 'manager'),
                            name='role', 
                            id=f'role-{user_id}'
                        ),
                        cls="form-row"
                    ),
                    Div(
                        Button('💾 Save Changes', type='submit'),
                        Button(
                            '❌ Cancel',
                            hx_get=f"/users/{user_id}/card",
                            hx_target=f"#user-{user_id}",
                            hx_swap='outerHTML',
                            type='button',
                            style="background: #6c757d;"
                        ),
                        cls="btn-group"
                    ),
                    hx_patch=f"/users/{user_id}/update",
                    hx_target=f"#user-{user_id}",
                    hx_swap='outerHTML'
                ),
                id=f'user-{user_id}',
                cls="card",
                style='border-left: 4px solid #ff9800;'
            )
        except Exception as e:
            return P(f'Error: {str(e)}')

    @rt('/users/{user_id}/update')
    def patch(user_id: str, email: str, full_name: str = None, role: str = 'user'):
        try:
            resp = http_client.patch(f'/users/{user_id}', json={
                "email": email,
                "full_name": full_name,
                "role": role
            })
            
            if resp.status_code == 200:
                data = _safe_json(resp)
                if data:
                    return user_card(data)
                return P("Updated, but server returned no JSON.", style='color: #ffc107;')
            
            data = _safe_json(resp) or {}
            return P(f"Error: {data.get('detail', 'Update failed')}", style='color: #dc3545;')
        except Exception as e:
            return P(f'Error: {str(e)}', style='color: #dc3545;')

    @rt('/users/{user_id}/card')
    def get(user_id: str):
        try:
            resp = http_client.get(f'/users/{user_id}')
            if resp.status_code == 200:
                return user_card(resp.json())
            return P('User not found')
        except Exception as e:
            return P(f'Error: {str(e)}')

    @rt('/users/{user_id}/documents')
    def get(user_id: str):
        try:
            resp = http_client.get(f'/users/{user_id}')
            if resp.status_code != 200:
                return Titled('Error', P('User not found'))
            
            user = resp.json()
            permissions = user.get('permissions', [])
            
            # Get documents from permissions
            doc_ids = [p['document_id'] for p in permissions]
            docs = []
            for doc_id in doc_ids:
                try:
                    doc_resp = http_client.get(f'/documents/{doc_id}')
                    if doc_resp.status_code == 200:
                        docs.append(doc_resp.json())
                except:
                    pass
            
            return Div(
                navbar('users'),
                Titled(
                    f"📄 Documents for {user.get('full_name', user['email'])}",
                    Div(
                        H3(f"Accessible Documents ({len(docs)})"),
                        Div(
                            *[
                                Div(
                                    H4(doc['title']),
                                    P(Strong('Status: '), 
                                      Span(doc.get('status', 'Unknown'), cls=f"badge badge-{doc.get('status', '').lower()}")
                                    ),
                                    P(Strong('Created: '), _fmt_date(doc.get('created_at'))),
                                    Button(
                                        'View Document',
                                        onclick=f"window.location='/documents/{doc['id']}'"
                                    ),
                                    cls="card",
                                    style='border-left: 4px solid #28a745;'
                                ) for doc in docs
                            ] if docs else P('No documents accessible to this user'),
                        ),
                        cls="card"
                    ),
                    Div(
                        A('← Back to Users', href='/users', style="text-decoration: none; color: #0066cc; font-weight: 600;"),
                        style='margin-top: 2rem;'
                    )
                )
            )
        except Exception as e:
            return Titled('Error', P(f'Error: {str(e)}'))


def user_card(user: dict):
    created = _parse_dt(user.get('created_at'))
    updated = _parse_dt(user.get('updated_at'))
    role = (user.get('role') or 'user').upper()
    role_color = '#dc3545' if role == 'ADMIN' else '#28a745' if role == 'MANAGER' else '#0066cc'
    
    return Div(
        Div(
            H4(user.get('full_name') or 'No Name', style="margin-bottom: 0.5rem;"),
            P(
                Strong("Email: "), user['email'],
                style="margin: 0.25rem 0;"
            ),
            P(
                Strong("Role: "),
                Span(role, style=f"color: {role_color}; font-weight: 600;"),
                style="margin: 0.25rem 0;"
            ),
            P(
                Strong("Created: "),
                created.strftime('%Y-%m-%d %H:%M') if created else '—',
                style="margin: 0.25rem 0;"
            ),
            Details(
                Summary("👁️ More Details"),
                P(Strong("ID: "), user['id'], style="font-size: 0.9em; color: #666;"),
                P(Strong("Updated: "), updated.strftime('%Y-%m-%d %H:%M') if updated else '—', style="font-size: 0.9em; color: #666;"),
                Div(
                    Button(
                        "✏️ Edit",
                        hx_get=f"/users/{user['id']}/edit",
                        hx_target=f"#user-{user['id']}",
                        hx_swap="outerHTML"
                    ),
                    Button(
                        "📄 View Documents",
                        onclick=f"window.location='/users/{user['id']}/documents'",
                        style="background: #28a745;"
                    ),
                    cls="btn-group"
                ),
                style="margin-top: 1rem;"
            ),
            id=f"user-{user['id']}"
        ),
        cls="card",
        style="border-left: 4px solid #9c27b0;"
    )


def _parse_dt(val: str | None):
    if not val:
        return None
    try:
        return datetime.fromisoformat(val.replace('Z', '+00:00'))
    except Exception:
        return None


def _fmt_date(val: str | None):
    if not val:
        return '—'
    try:
        return datetime.fromisoformat(val.replace('Z', '+00:00')).strftime('%Y-%m-%d')
    except Exception:
        return '—'