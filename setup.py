import os
from dotenv import load_dotenv
from sqlalchemy import text
from models import engine, init_db

load_dotenv()

def create_storage_bucket():
    """Create Supabase storage bucket for PDFs"""
    bucket_name = os.getenv('BUCKET_NAME', 'pdfs')
    
    try:
        with engine.connect() as conn:
            # Check if bucket exists
            result = conn.execute(text(
                "SELECT id FROM storage.buckets WHERE id = :bucket_id"
            ), {"bucket_id": bucket_name})
            
            if result.fetchone():
                print(f"✓ Bucket '{bucket_name}' already exists")
            else:
                # Create bucket
                conn.execute(text("""
                    INSERT INTO storage.buckets (id, name, public)
                    VALUES (:bucket_id, :bucket_name, true)
                """), {"bucket_id": bucket_name, "bucket_name": bucket_name})
                conn.commit()
                print(f"✓ Created bucket '{bucket_name}'")
                
    except Exception as e:
        print(f"⚠ Bucket creation skipped: {e}")

def setup():
    """Run complete setup"""
    print("=== Setting up database ===")
    
    # Create tables
    init_db()
    
    # Create storage bucket
    create_storage_bucket()
    
    print("\n=== Setup complete ===")
    print("\nNext steps:")
    print("1. Run: uvicorn app:app --reload")
    print("2. Visit: http://localhost:8000/docs")

if __name__ == "__main__":
    setup()