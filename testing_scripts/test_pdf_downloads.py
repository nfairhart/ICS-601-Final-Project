import requests
import time
import os

papers = ["1706.03762", "1412.6980", "2005.14165", "1312.6114", "1710.10903"]
os.makedirs("rag_test_pdfs", exist_ok=True)

for paper_id in papers:
    for v in range(1, 4):
        url = f"https://arxiv.org/pdf/{paper_id}v{v}.pdf"
        print(f"Downloading {paper_id} v{v}...")
        response = requests.get(url)
        with open(f"rag_test_pdfs/{paper_id}_v{v}.pdf", 'wb') as f:
            f.write(response.content)
        time.sleep(3) # Polite delay for arXiv servers