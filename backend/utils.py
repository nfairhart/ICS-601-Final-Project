import os
import requests
from dotenv import load_dotenv
from markitdown import MarkItDown
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
    """Parse PDF to markdown using MarkItDown"""
    try:
        md = MarkItDown()
        result = md.convert(pdf_path)
        #print(result.markdown)
        return result.markdown
    except Exception as e:
        raise Exception(f"Failed to convert PDF to markdown: {str(e)}")

def process_pdf_upload(pdf_path: str, document_id: str, filename: str) -> tuple[str, str]:
    """
    Process a PDF file: convert to markdown and upload to Supabase storage.

    Args:
        pdf_path: Local path to the PDF file
        document_id: UUID of the document
        filename: Original filename of the PDF

    Returns:
        tuple: (markdown_content, pdf_url)
    """
    # Convert PDF to markdown
    markdown_content = parse_pdf_to_markdown(pdf_path)

    # Upload PDF to Supabase storage
    # Use document_id as folder to organize PDFs
    destination_path = f"{document_id}/{filename}"
    pdf_url = upload_pdf(pdf_path, destination_path)

    return markdown_content, pdf_url