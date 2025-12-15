from fasthtml.common import *
from frontend.lib.api import http_client
from frontend.components.users import user_card
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
                "User Management",
                Card(
                    H3("Create New User"),
                    Form(
                        Div(Label("Email:", For="email"), Input(type="email", name="email", id="email", required=True, placeholder="user@example.com")),
                        Div(Label("Full Name:", For="full_name"), Input(type="text", name="full_name", id="full_name", placeholder="John Doe")),
                        Div(
                            Label("Role:", For="role"),
                            Select(
                                Option("User", value="user", selected=True),
                                Option("Admin", value="admin"),
                                Option("Manager", value="manager"),
                                name="role", id="role"
                            )
                        ),
                        Button("Create User", type="submit"),
                        hx_post="/users/create",
                        hx_target="#users-list",
                        hx_swap="outerHTML"
                    ),
                ),
            ),
            Div(
                H3("Existing Users"),
                Div(
                    *[user_card(u) for u in users] if users else P("No users found. Create one above!"),
                    id="users-list"
                )
            )
        )

    @rt('/users/create')
    async def post(email: str, full_name: str = None, role: str = 'user'):
        try:
            resp = http_client.post('/users', json={"email": email, "full_name": full_name, "role": role})
            if resp.status_code in (200, 201):
                users_resp = http_client.get('/users')
                users = _safe_json(users_resp) if users_resp.status_code == 200 else []
                return Div(P("✓ User created successfully!", style="color: green;"), *[user_card(u) for u in users], id="users-list")
            else:
                data = _safe_json(resp) or {}
                detail = data.get('detail') or (resp.text.strip() or 'Unknown error')
                return Div(P(f"✗ Error: {detail}", style="color: red;"), id="users-list")
        except Exception as e:
            return Div(P(f"✗ Error connecting to API: {str(e)}", style="color: red;"), id="users-list")

    @rt('/users/{user_id}/edit')
    def get(user_id: str):
        try:
            resp = http_client.get(f'/users/{user_id}')
            if resp.status_code != 200:
                return P('User not found')
            user = resp.json()
            return Card(
                H4('Edit User'),
                Form(
                    Input(type='hidden', name='user_id', value=user_id),
                    Div(Label('Email:', For=f'email-{user_id}'), Input(type='email', name='email', id=f'email-{user_id}', value=user['email'], required=True)),
                    Div(Label('Full Name:', For=f'full_name-{user_id}'), Input(type='text', name='full_name', id=f'full_name-{user_id}', value=user.get('full_name', ''))),
                    Div(Label('Role:', For=f'role-{user_id}'),
                        Select(
                            Option('User', value='user', selected=user.get('role') == 'user'),
                            Option('Admin', value='admin', selected=user.get('role') == 'admin'),
                            Option('Manager', value='manager', selected=user.get('role') == 'manager'),
                            name='role', id=f'role-{user_id}'
                        )
                    ),
                    Div(
                        Button('Save Changes', type='submit'),
                        Button('Cancel', hx_get=f"/users/{user_id}/card", hx_target=f"#user-{user_id}", hx_swap='outerHTML', type='button'),
                        style='display: flex; gap: 0.5rem;'
                    ),
                    hx_patch=f"/users/{user_id}/update",
                    hx_target=f"#user-{user_id}",
                    hx_swap='outerHTML'
                ),
                id=f'user-{user_id}',
                style='border-left: 4px solid #ff9900; padding: 1rem;'
            )
        except Exception as e:
            return P(f'Error: {str(e)}')

    @rt('/users/{user_id}/update')
    def patch(user_id: str, email: str, full_name: str = None, role: str = 'user'):
        try:
            resp = http_client.patch(f'/users/{user_id}', json={"email": email, "full_name": full_name, "role": role})
            if resp.status_code == 200:
                data = _safe_json(resp)
                if data:
                    return user_card(data)
                return P("Updated, but server returned no JSON.", style='color: orange;')
            data = _safe_json(resp) or {}
            return P(f"Error: {data.get('detail', 'Update failed')}", style='color: red;')
        except Exception as e:
            return P(f'Error: {str(e)}', style='color: red;')

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
            documents = user.get('documents', [])
            return Titled(f"Documents for {user.get('full_name', user['email'])}",
                Card(
                    H3('Accessible Documents'),
                    Div(
                        *[
                            Card(
                                H4(doc['title']),
                                P(Strong('Status: '), doc.get('status', 'Unknown')),
                                P(Strong('Created: '), _fmt_date(doc.get('created_at'))),
                                style='border-left: 3px solid #28a745;'
                            ) for doc in documents
                        ] if documents else P('No documents accessible to this user')
                    )
                ),
                Div(A('← Back to Users', href='/users'), style='margin-top: 2rem;')
            )
        except Exception as e:
            return Titled('Error', P(f'Error: {str(e)}'))


def _fmt_date(val: str | None):
    if not val:
        return '—'
    try:
        return datetime.fromisoformat(val.replace('Z', '+00:00')).strftime('%Y-%m-%d')
    except Exception:
        return '—'