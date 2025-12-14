from dotenv import load_dotenv
import os
import requests

# Load environment variables
load_dotenv()

def upload_pdf(file_path, destination_path):
    """Simple upload function using .env credentials"""
    
    # Get credentials from environment
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    bucket_name = os.getenv('BUCKET_NAME', 'pdfs')
    
    # Validate
    if not supabase_url or not supabase_key:
        raise ValueError("Missing credentials in .env file")
    
    # Upload
    url = f"{supabase_url}/storage/v1/object/{bucket_name}/{destination_path}"
    headers = {
        "Authorization": f"Bearer {supabase_key}",
        "apikey": supabase_key
    }
    
    with open(file_path, 'rb') as f:
        files = {'file': (os.path.basename(file_path), f, 'application/pdf')}
        response = requests.post(url, headers=headers, files=files)
    
    if response.status_code in [200, 201]:
        print(f"✓ Upload successful!")
        return response.json()
    else:
        print(f"✗ Upload failed: {response.status_code}")
        print(response.text)
        return None

# Usage
if __name__ == "__main__":
    upload_pdf("document.pdf", "uploads/document.pdf")