import httpx

API_BASE_URL = "http://localhost:8000"

http_client = httpx.Client(base_url=API_BASE_URL, timeout=10)
