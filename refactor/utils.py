import os
import requests
from dotenv import load_dotenv

load_dotenv()

def upload_pdf(file_path: str, destination_path: str) -> str:
    """Upload PDF to Supabase storage"""
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    bucket_name = os.getenv('BUCKET_NAME', 'pdfs')
    
    if not supabase_url or not supabase_key:
        raise ValueError("Missing SUPABASE_URL or SUPABASE_KEY in .env")
    
    url = f"{supabase_url}/storage/v1/object/{bucket_name}/{destination_path}"
    headers = {
        "Authorization": f"Bearer {supabase_key}",
        "apikey": supabase_key
    }
    
    with open(file_path, 'rb') as f:
        files = {'file': (os.path.basename(file_path), f, 'application/pdf')}
        response = requests.post(url, headers=headers, files=files)
    
    if response.status_code in [200, 201]:
        # Return public URL
        return f"{supabase_url}/storage/v1/object/public/{bucket_name}/{destination_path}"
    else:
        raise Exception(f"Upload failed: {response.status_code} - {response.text}")

def download_pdf(pdf_url: str, save_path: str):
    """Download PDF from URL"""
    response = requests.get(pdf_url)
    response.raise_for_status()
    
    with open(save_path, 'wb') as f:
        f.write(response.content)
    
    return save_path

def parse_pdf_to_markdown(pdf_path: str) -> str:
    """Parse PDF to markdown (placeholder - implement with your preferred parser)"""
    # TODO: Implement with pymupdf, pdfplumber, or similar
    # For now, return placeholder
    return f"# Parsed content from {pdf_path}\n\nImplement PDF parsing here."