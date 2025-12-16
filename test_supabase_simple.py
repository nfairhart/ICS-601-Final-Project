"""
Ultra-simple Supabase storage test.
Uploads a tiny text file to verify connectivity.
"""

import os
from dotenv import load_dotenv
import requests

load_dotenv()

def test_supabase():
    """Test Supabase storage with minimal setup"""

    print("\n" + "="*60)
    print("SUPABASE STORAGE CONNECTION TEST")
    print("="*60 + "\n")

    # Load config
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    bucket_name = os.getenv('BUCKET_NAME', 'pdfs')

    # Display config
    print("Configuration:")
    if supabase_url:
        print(f"  ✓ SUPABASE_URL: {supabase_url}")
    else:
        print("  ✗ SUPABASE_URL: NOT SET")

    if supabase_key:
        # Show first and last few characters
        masked = f"{supabase_key[:15]}...{supabase_key[-10:]}"
        print(f"  ✓ SUPABASE_KEY: {masked}")
    else:
        print("  ✗ SUPABASE_KEY: NOT SET")

    print(f"  ✓ BUCKET_NAME: {bucket_name}")

    # Check credentials
    if not supabase_url or not supabase_key:
        print("\n❌ Missing credentials!")
        print("\nAdd to .env file:")
        print("SUPABASE_URL=https://your-project.supabase.co")
        print("SUPABASE_KEY=your_service_role_key_here")
        return False

    # Create test content (plain text)
    test_content = b"Hello from Supabase storage test!"
    filename = "test-upload.txt"

    # Build URL
    url = f"{supabase_url}/storage/v1/object/{bucket_name}/test/{filename}"

    print(f"\nUpload endpoint:")
    print(f"  {url}")

    # Prepare request
    headers = {
        "Authorization": f"Bearer {supabase_key}",
        "apikey": supabase_key,
        "Content-Type": "text/plain"
    }

    print(f"\nAttempting upload...")

    try:
        # Make request
        response = requests.post(url, data=test_content, headers=headers, timeout=10)

        print(f"\nStatus: {response.status_code}")

        if response.status_code in [200, 201]:
            print("✅ SUCCESS!")
            print(f"\nFile uploaded to: {bucket_name}/test/{filename}")

            # Show public URL
            public_url = f"{supabase_url}/storage/v1/object/public/{bucket_name}/test/{filename}"
            print(f"Public URL: {public_url}")

            return True

        else:
            print(f"❌ FAILED with status {response.status_code}")
            print(f"\nResponse: {response.text}")

            # Specific error guidance
            if response.status_code == 404:
                print(f"\n💡 Bucket '{bucket_name}' doesn't exist!")
                print("\nTo create it:")
                print(f"  1. Go to your Supabase dashboard")
                print(f"  2. Storage → Create new bucket")
                print(f"  3. Name it '{bucket_name}'")
                print(f"  4. Make it public if you want public URLs")
                print(f"\nOr run: python3 -m backend.setup")

            elif response.status_code == 401:
                print(f"\n💡 Authentication failed!")
                print("\nCheck:")
                print("  - SUPABASE_KEY is the 'service_role' key (not anon)")
                print("  - Key is copied correctly without extra spaces")
                print("  - .env file is in the project root")

            elif response.status_code == 400:
                print(f"\n💡 Bad request!")
                print("  - Bucket name might be invalid")
                print("  - Check bucket permissions")

            return False

    except requests.exceptions.ConnectionError:
        print("❌ Connection failed!")
        print("\n💡 Possible causes:")
        print("  - No internet connection")
        print("  - SUPABASE_URL is incorrect")
        print("  - Firewall blocking request")
        return False

    except requests.exceptions.Timeout:
        print("❌ Request timed out!")
        return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_supabase()

    print("\n" + "="*60)
    if success:
        print("✅ Supabase storage is working!")
        print("\nYou can now test PDF uploads:")
        print("  python3 test_supabase_upload.py")
    else:
        print("❌ Fix the issues above and try again")
        print("\nNeed help?")
        print("  - Check Supabase dashboard for bucket")
        print("  - Verify .env credentials")
        print("  - See TROUBLESHOOTING.md")
    print("="*60 + "\n")
