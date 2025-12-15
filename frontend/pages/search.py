from fasthtml.common import *
from frontend.lib.api import http_client
from frontend.components.navbar import navbar


def register(rt):
    @rt('/search')
    def get():
        # Preload users so we can search with that user's permissions
        try:
            users_resp = http_client.get('/users')
            users = users_resp.json() if users_resp.status_code == 200 else []
        except Exception:
            users = []

        return Div(
            navbar('search'),
            Titled('RAG Search',
                Card(
                    Form(
                        Div(Label('Query:', For='query'), Input(type='text', id='query', name='query', required=True, placeholder='Ask about documents...')),
                        Div(Label('User:', For='user_id'),
                            Select(
                                *[Option(u.get('full_name') or u['email'], value=u['id']) for u in users],
                                id='user_id', name='user_id', required=True
                            )
                        ),
                        Div(Label('Top K:', For='top_k'), Input(type='number', id='top_k', name='top_k', value='5', min='1', max='20')),
                        Button('Search', type='submit'),
                        hx_post='/search/run',
                        hx_target='#search-results',
                        hx_swap='innerHTML'
                    )
                ),
                Div(id='search-results')
            )
        )

    @rt('/search/run')
    async def post(query: str, user_id: str, top_k: int = 5):
        try:
            resp = http_client.post('/search', json={
                'query': query,
                'user_id': user_id,
                'top_k': top_k
            })
            if resp.status_code != 200:
                return P('Search failed', style='color: red;')
            data = resp.json()
            results = data.get('results', [])
            if not results:
                return P('No results found.')
            return Div(
                *[search_result_card(r) for r in results]
            )
        except Exception as e:
            return P(f'Error: {str(e)}', style='color: red;')


def search_result_card(r: dict):
    score = r.get('relevance_score') or r.get('relevance') or 0
    title = r.get('title') or 'Untitled'
    content = r.get('content') or ''
    doc_id = r.get('document_id')
    return Card(
        H4(title),
        P(Strong('Relevance: '), f"{score:.2f}" if isinstance(score, (int, float)) else str(score)),
        P(content[:500] + ('...' if len(content) > 500 else '')),
        Div(Button('Open Document', onclick=f"window.location='/documents/{doc_id}'"))
    )
