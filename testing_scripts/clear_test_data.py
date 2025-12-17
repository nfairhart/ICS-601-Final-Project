"""
Clear all test data from database and Supabase storage bucket.

This script:
1. Deletes all records from database tables (in correct order to respect foreign keys)
2. Clears all files from the Supabase storage bucket
3. Resets the database to a clean state for testing

WARNING: This will delete ALL data from your database and storage bucket!
"""

import os
import sys
import requests
from dotenv import load_dotenv
from sqlalchemy import text
from backend.database import engine

load_dotenv()


class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_section(title: str):
    """Print a formatted section header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{title}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")


def print_success(message: str):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {message}{Colors.ENDC}")


def print_error(message: str):
    """Print error message"""
    print(f"{Colors.RED}✗ {message}{Colors.ENDC}")


def print_warning(message: str):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠ {message}{Colors.ENDC}")


def print_info(message: str):
    """Print info message"""
    print(f"{Colors.CYAN}ℹ {message}{Colors.ENDC}")


def confirm_deletion():
    """Ask user to confirm deletion"""
    print_warning("This will DELETE ALL data from your database and storage bucket!")
    print_warning("This action cannot be undone.")

    response = input(f"\n{Colors.YELLOW}Are you sure you want to continue? (yes/no): {Colors.ENDC}")

    if response.lower() not in ['yes', 'y']:
        print_info("Operation cancelled.")
        sys.exit(0)

    print()


def clear_database_tables():
    """Clear all tables in the correct order to respect foreign key constraints"""
    print_section("Clearing Database Tables")

    try:
        with engine.connect() as conn:
            # Delete in order: permissions, versions, documents, users
            # This order respects foreign key constraints

            print_info("Deleting document permissions...")
            result = conn.execute(text("DELETE FROM document_permissions"))
            conn.commit()
            print_success(f"Deleted {result.rowcount} document permissions")

            print_info("Deleting document versions...")
            result = conn.execute(text("DELETE FROM document_versions"))
            conn.commit()
            print_success(f"Deleted {result.rowcount} document versions")

            print_info("Deleting documents...")
            result = conn.execute(text("DELETE FROM documents"))
            conn.commit()
            print_success(f"Deleted {result.rowcount} documents")

            print_info("Deleting users...")
            result = conn.execute(text("DELETE FROM users"))
            conn.commit()
            print_success(f"Deleted {result.rowcount} users")

            print_success("All database tables cleared successfully!")

    except Exception as e:
        print_error(f"Failed to clear database tables: {str(e)}")
        return False

    return True


def clear_storage_bucket():
    """Clear all files from Supabase storage bucket"""
    print_section("Clearing Supabase Storage Bucket")

    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    bucket_name = os.getenv('BUCKET_NAME', 'pdfs')

    if not supabase_url or not supabase_key:
        print_warning("Missing SUPABASE_URL or SUPABASE_KEY - skipping storage cleanup")
        return True

    try:
        # List all files in bucket
        list_url = f"{supabase_url}/storage/v1/object/list/{bucket_name}"
        headers = {
            "Authorization": f"Bearer {supabase_key}",
            "apikey": supabase_key
        }

        # List files (empty prefix to get all)
        list_response = requests.post(
            list_url,
            headers=headers,
            json={"limit": 1000, "offset": 0, "sortBy": {"column": "name", "order": "asc"}}
        )

        if list_response.status_code == 200:
            files = list_response.json()

            if not files:
                print_info(f"Bucket '{bucket_name}' is already empty")
                return True

            print_info(f"Found {len(files)} files/folders in bucket")

            # Delete all files
            deleted_count = 0
            failed_count = 0

            for file_obj in files:
                file_path = file_obj.get('name')

                # If it's a folder, we need to list and delete its contents
                if file_obj.get('id') is None:
                    # This is a folder/prefix
                    print_info(f"Clearing folder: {file_path}")

                    # List files in this folder
                    folder_response = requests.post(
                        list_url,
                        headers=headers,
                        json={
                            "limit": 1000,
                            "offset": 0,
                            "prefix": file_path,
                            "sortBy": {"column": "name", "order": "asc"}
                        }
                    )

                    if folder_response.status_code == 200:
                        folder_files = folder_response.json()

                        for folder_file in folder_files:
                            if folder_file.get('id'):  # Only delete actual files, not folders
                                file_to_delete = folder_file.get('name')

                                delete_url = f"{supabase_url}/storage/v1/object/{bucket_name}/{file_to_delete}"
                                delete_response = requests.delete(delete_url, headers=headers)

                                if delete_response.status_code in [200, 204]:
                                    deleted_count += 1
                                    print(f"  ✓ Deleted: {file_to_delete}")
                                else:
                                    failed_count += 1
                                    print_error(f"  Failed to delete: {file_to_delete}")
                else:
                    # This is a file at root level
                    delete_url = f"{supabase_url}/storage/v1/object/{bucket_name}/{file_path}"
                    delete_response = requests.delete(delete_url, headers=headers)

                    if delete_response.status_code in [200, 204]:
                        deleted_count += 1
                        print(f"  ✓ Deleted: {file_path}")
                    else:
                        failed_count += 1
                        print_error(f"  Failed to delete: {file_path}")

            if failed_count == 0:
                print_success(f"Successfully deleted all {deleted_count} files from bucket '{bucket_name}'")
            else:
                print_warning(f"Deleted {deleted_count} files, {failed_count} failed")

        else:
            print_error(f"Failed to list bucket files: {list_response.status_code} - {list_response.text}")
            return False

    except Exception as e:
        print_error(f"Failed to clear storage bucket: {str(e)}")
        return False

    return True


def verify_cleanup():
    """Verify that cleanup was successful"""
    print_section("Verifying Cleanup")

    try:
        with engine.connect() as conn:
            # Check each table
            tables = ['users', 'documents', 'document_versions', 'document_permissions']

            for table in tables:
                result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = result.scalar()

                if count == 0:
                    print_success(f"Table '{table}': 0 records")
                else:
                    print_warning(f"Table '{table}': {count} records remaining")

            print_success("\nDatabase cleanup verified!")

    except Exception as e:
        print_error(f"Verification failed: {str(e)}")


def main():
    """Main cleanup execution"""
    print_section("Database and Storage Cleanup Script")

    # Confirm with user
    confirm_deletion()

    # Clear database
    db_success = clear_database_tables()

    # Clear storage
    storage_success = clear_storage_bucket()

    # Verify cleanup
    if db_success:
        verify_cleanup()

    # Summary
    print_section("Cleanup Summary")

    if db_success and storage_success:
        print_success("All cleanup operations completed successfully!")
        print_info("\nYou can now run the test script:")
        print(f"  {Colors.CYAN}python test_backend.py{Colors.ENDC}")
    else:
        print_error("Some cleanup operations failed. Please review the errors above.")
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_warning("\n\nCleanup interrupted by user")
        sys.exit(0)
    except Exception as e:
        print_error(f"\n\nUnexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
