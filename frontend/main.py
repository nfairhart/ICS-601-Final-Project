from fasthtml.common import *
from frontend.pages.home import register as register_home
from frontend.pages.users import register as register_users
from frontend.pages.documents import register as register_documents
from frontend.pages.search import register as register_search
import uvicorn


app, rt = fast_app(
    hdrs=(
        Link(rel='stylesheet', href='https://cdn.jsdelivr.net/npm/water.css@2/out/water.css'),
    )
)

# Register routes from pages
register_home(rt)
register_users(rt)
register_documents(rt)
register_search(rt)

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=5001)
