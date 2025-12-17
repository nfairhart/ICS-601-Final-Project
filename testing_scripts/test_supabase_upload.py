"""
Simple test script to verify Supabase storage upload is working.
This creates a test PDF and uploads it directly to Supabase storage.
"""

import os
import io
from dotenv import load_dotenv
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
import requests

load_dotenv()

def print_step(step_num, message):
    """Print a numbered step"""
    print(f"\n{'='*60}")
    print(f"Step {step_num}: {message}")
    print(f"{'='*60}")

def generate_test_pdf():
    """Generate a simple test PDF"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()

    story = [
        Paragraph("Test PDF Document", styles['Title']),
        Paragraph("This is a test PDF to verify Supabase storage upload.", styles['Normal'])
    ]

    doc.build(story)
    buffer.seek(0)
    return buffer.read()

def upload_to_supabase(pdf_bytes, filename):
    """Upload PDF to Supabase storage bucket"""

    # Get credentials from .env
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    bucket_name = os.getenv('BUCKET_NAME', 'pdfs')

    print(f"\nConfiguration:")
    print(f"  SUPABASE_URL: {supabase_url[:30]}..." if supabase_url else "  SUPABASE_URL: NOT SET")
    print(f"  SUPABASE_KEY: {supabase_key[:20]}..." if supabase_key else "  SUPABASE_KEY: NOT SET")
    print(f"  BUCKET_NAME: {bucket_name}")

    if not supabase_url or not supabase_key:
        print("\n❌ ERROR: Missing Supabase credentials in .env file!")
        print("\nPlease add to your .env file:")
        print("  SUPABASE_URL=https://your-project.supabase.co")
        print("  SUPABASE_KEY=your_supabase_key")
        print("  BUCKET_NAME=pdfs")
        return False

    # Construct upload URL
    destination_path = f"test/{filename}"
    url = f"{supabase_url}/storage/v1/object/{bucket_name}/{destination_path}"

    print(f"\nUpload URL: {url}")

    # Prepare headers
    headers = {
        "Authorization": f"Bearer {supabase_key}",
        "apikey": supabase_key,
        "Content-Type": "application/pdf"
    }

    # Upload the file
    print(f"\nUploading PDF ({len(pdf_bytes)} bytes)...")

    try:
        response = requests.post(
            url,
            data=pdf_bytes,
            headers=headers,
            timeout=30
        )

        print(f"\nResponse Status Code: {response.status_code}")
        print(f"Response Body: {response.text[:500]}")

        if response.status_code in [200, 201]:
            print("\n✅ SUCCESS! PDF uploaded to Supabase storage")

            # Construct public URL
            public_url = f"{supabase_url}/storage/v1/object/public/{bucket_name}/{destination_path}"
            print(f"\nPublic URL: {public_url}")
            print("\nYou can verify the upload by:")
            print(f"  1. Opening the URL above in your browser")
            print(f"  2. Checking your Supabase dashboard → Storage → {bucket_name}")

            return True
        else:
            print(f"\n❌ FAILED! Upload returned status {response.status_code}")

            # Parse error details
            try:
                error_data = response.json()
                print(f"\nError details: {error_data}")
            except:
                pass

            # Common error solutions
            print("\n💡 Common solutions:")
            if response.status_code == 401:
                print("  - Check that SUPABASE_KEY is correct")
                print("  - Use the 'service_role' key for testing (not anon key)")
            elif response.status_code == 404:
                print(f"  - Bucket '{bucket_name}' may not exist")
                print("  - Create it in Supabase dashboard → Storage")
                print("  - Or run: python3 -m backend.setup")
            elif response.status_code == 400:
                print("  - Check bucket name is correct")
                print("  - Verify bucket is configured to accept uploads")

            return False

    except requests.exceptions.Timeout:
        print("\n❌ FAILED! Request timed out after 30 seconds")
        return False
    except requests.exceptions.ConnectionError as e:
        print(f"\n❌ FAILED! Connection error: {e}")
        print("\n💡 Possible causes:")
        print("  - Check your internet connection")
        print("  - Verify SUPABASE_URL is correct")
        print("  - Check if Supabase service is accessible")
        return False
    except Exception as e:
        print(f"\n❌ FAILED! Unexpected error: {e}")
        return False

def main():
    """Main test execution"""
    print("\n" + "="*60)
    print("SUPABASE STORAGE UPLOAD TEST")
    print("="*60)

    # Step 1: Generate test PDF
    print_step(1, "Generating Test PDF")
    try:
        pdf_bytes = generate_test_pdf()
        print(f"✅ Generated test PDF ({len(pdf_bytes)} bytes)")
    except Exception as e:
        print(f"❌ Failed to generate PDF: {e}")
        print("\n💡 Make sure reportlab is installed:")
        print("   pip3 install reportlab")
        return

    # Step 2: Upload to Supabase
    print_step(2, "Uploading to Supabase Storage")
    filename = "test_upload.pdf"
    success = upload_to_supabase(pdf_bytes, filename)

    # Step 3: Summary
    print_step(3, "Test Summary")
    if success:
        print("✅ All tests passed!")
        print("\nYour Supabase storage is configured correctly.")
        print("You can now run the full test suite:")
        print("  python3 test_backend.py --clear")
    else:
        print("❌ Test failed!")
        print("\nPlease fix the issues above before running the full test suite.")
        print("\nQuick fixes:")
        print("  1. Verify .env file has correct Supabase credentials")
        print("  2. Create the 'pdfs' bucket in Supabase dashboard")
        print("  3. Use the 'service_role' key (not anon key)")

    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    main()
