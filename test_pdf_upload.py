"""
Simple diagnostic script to test PDF upload functionality.
This helps debug issues with the PDF upload endpoint.
"""

import requests
import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

BASE_URL = "http://localhost:8000"

def generate_simple_pdf() -> bytes:
    """Generate a very simple PDF for testing"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = [Paragraph("Test PDF Document", styles['Title'])]
    doc.build(story)
    buffer.seek(0)
    return buffer.read()

def test_pdf_upload():
    """Test the PDF upload endpoint with minimal setup"""

    print("=" * 60)
    print("PDF Upload Diagnostic Test")
    print("=" * 60)

    # Step 1: Check API health
    print("\n1. Checking API health...")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("   ✓ API is running")
        else:
            print(f"   ✗ API returned status {response.status_code}")
            return
    except requests.exceptions.ConnectionError:
        print(f"   ✗ Could not connect to {BASE_URL}")
        print("   → Make sure FastAPI is running: uvicorn backend.app:app --reload")
        return

    # Step 2: Create a test user
    print("\n2. Creating test user...")
    user_response = requests.post(
        f"{BASE_URL}/users",
        json={"email": "test@example.com", "full_name": "Test User", "role": "admin"}
    )

    if user_response.status_code == 201:
        user = user_response.json()
        print(f"   ✓ Created user: {user['id']}")
    elif user_response.status_code == 400 and "already exists" in user_response.text:
        # User already exists, fetch it
        users_response = requests.get(f"{BASE_URL}/users")
        users = users_response.json()
        user = next((u for u in users if u['email'] == 'test@example.com'), None)
        if user:
            print(f"   ℹ Using existing user: {user['id']}")
        else:
            print("   ✗ Could not find or create user")
            return
    else:
        print(f"   ✗ Failed to create user: {user_response.status_code}")
        print(f"      {user_response.text}")
        return

    # Step 3: Create a test document
    print("\n3. Creating test document...")
    doc_response = requests.post(
        f"{BASE_URL}/documents",
        json={
            "title": "PDF Upload Test Document",
            "description": "Testing PDF upload",
            "created_by": user['id']
        }
    )

    if doc_response.status_code == 200:
        doc = doc_response.json()
        print(f"   ✓ Created document: {doc['id']}")
    else:
        print(f"   ✗ Failed to create document: {doc_response.status_code}")
        print(f"      {doc_response.text}")
        return

    # Step 4: Generate PDF
    print("\n4. Generating test PDF...")
    try:
        pdf_content = generate_simple_pdf()
        print(f"   ✓ Generated PDF ({len(pdf_content)} bytes)")
    except Exception as e:
        print(f"   ✗ Failed to generate PDF: {e}")
        return

    # Step 5: Upload PDF
    print("\n5. Uploading PDF to document...")
    print(f"   URL: {BASE_URL}/documents/{doc['id']}/upload-pdf")
    print(f"   Params: created_by={user['id']}, change_summary='Test upload'")

    files = {
        'pdf_file': ('test.pdf', io.BytesIO(pdf_content), 'application/pdf')
    }
    params = {
        'created_by': user['id'],
        'change_summary': 'Test upload'
    }

    try:
        upload_response = requests.post(
            f"{BASE_URL}/documents/{doc['id']}/upload-pdf",
            files=files,
            params=params,
            timeout=30
        )

        print(f"\n   Response Status: {upload_response.status_code}")

        if upload_response.status_code == 200:
            result = upload_response.json()
            print("   ✓ PDF uploaded successfully!")
            print(f"   Version ID: {result['version']['id']}")
            print(f"   Version Number: {result['version']['version_number']}")
            print(f"   PDF URL: {result['version']['pdf_url']}")
            print("\n" + "=" * 60)
            print("SUCCESS! PDF upload is working correctly.")
            print("=" * 60)
        else:
            print("   ✗ Upload failed")
            print(f"\n   Response Body:")
            try:
                error_json = upload_response.json()
                print(f"   {error_json}")
            except:
                print(f"   {upload_response.text}")

            print("\n" + "=" * 60)
            print("FAILED! Check the errors above.")
            print("=" * 60)
            print("\nDebugging tips:")
            print("1. Check the FastAPI server terminal for error details")
            print("2. Verify Supabase credentials in .env file:")
            print("   - SUPABASE_URL")
            print("   - SUPABASE_KEY")
            print("   - BUCKET_NAME")
            print("3. Verify MarkItDown is installed: pip install markitdown")
            print("4. Check database connection")

    except requests.exceptions.Timeout:
        print("   ✗ Request timed out (30s)")
        print("   → PDF processing may be taking too long")
    except Exception as e:
        print(f"   ✗ Request failed: {e}")

if __name__ == "__main__":
    test_pdf_upload()
