from fasthtml.common import *
from datetime import datetime


def user_card(user: dict):
    created = _parse_dt(user.get('created_at'))
    updated = _parse_dt(user.get('updated_at'))
    return Card(
        Div(
            H4(user.get('full_name') or 'No Name'),
            P(Strong("Email: "), user['email']),
            P(Strong("Role: "), (user.get('role') or 'user').upper()),
            P(Strong("Created: "), created.strftime('%Y-%m-%d %H:%M') if created else '—'),
            Details(
                Summary("User Details"),
                P(Strong("ID: "), user['id']),
                P(Strong("Updated: "), updated.strftime('%Y-%m-%d %H:%M') if updated else '—'),
                Div(
                    Button(
                        "Edit User",
                        hx_get=f"/users/{user['id']}/edit",
                        hx_target=f"#user-{user['id']}",
                        hx_swap="outerHTML"
                    ),
                    Button(
                        "View Documents",
                        onclick=f"window.location='/users/{user['id']}/documents'"
                    ),
                    style="display: flex; gap: 0.5rem;"
                )
            ),
            id=f"user-{user['id']}",
            style="border-left: 4px solid #0066cc; padding: 1rem;"
        )
    )


def _parse_dt(val: str | None):
    if not val:
        return None
    try:
        return datetime.fromisoformat(val.replace('Z', '+00:00'))
    except Exception:
        return None
