"""
Environment diagnostic script - checks if all required configuration is present.
Run this before testing to ensure everything is configured correctly.
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def check_env_var(var_name: str, required: bool = True) -> bool:
    """Check if environment variable exists and has a value"""
    value = os.getenv(var_name)

    if value:
        # Mask sensitive values
        if 'KEY' in var_name.upper() or 'PASSWORD' in var_name.upper():
            display_value = value[:10] + "..." if len(value) > 10 else "***"
        else:
            display_value = value

        print(f"{Colors.GREEN}✓{Colors.ENDC} {var_name}: {display_value}")
        return True
    else:
        if required:
            print(f"{Colors.RED}✗{Colors.ENDC} {var_name}: {Colors.RED}MISSING{Colors.ENDC}")
        else:
            print(f"{Colors.YELLOW}⚠{Colors.ENDC} {var_name}: Not set (optional)")
        return not required

def check_module(module_name: str, import_name: str = None) -> bool:
    """Check if a Python module is installed"""
    if import_name is None:
        import_name = module_name

    try:
        __import__(import_name)
        print(f"{Colors.GREEN}✓{Colors.ENDC} {module_name}: Installed")
        return True
    except ImportError:
        print(f"{Colors.RED}✗{Colors.ENDC} {module_name}: {Colors.RED}NOT INSTALLED{Colors.ENDC}")
        return False

def main():
    print(f"\n{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}Environment Configuration Check{Colors.ENDC}")
    print(f"{Colors.BOLD}{'='*60}{Colors.ENDC}\n")

    all_good = True

    # Check database configuration
    print(f"{Colors.CYAN}{Colors.BOLD}Database Configuration:{Colors.ENDC}")
    all_good &= check_env_var('user', required=True)
    all_good &= check_env_var('password', required=True)
    all_good &= check_env_var('host', required=True)
    all_good &= check_env_var('port', required=True)
    all_good &= check_env_var('dbname', required=True)

    # Check Supabase configuration
    print(f"\n{Colors.CYAN}{Colors.BOLD}Supabase Storage Configuration:{Colors.ENDC}")
    all_good &= check_env_var('SUPABASE_URL', required=True)
    all_good &= check_env_var('SUPABASE_KEY', required=True)
    all_good &= check_env_var('BUCKET_NAME', required=False)

    # Check AI configuration
    print(f"\n{Colors.CYAN}{Colors.BOLD}AI/RAG Configuration:{Colors.ENDC}")
    all_good &= check_env_var('OPENAI_API_KEY', required=True)

    # Check required Python modules
    print(f"\n{Colors.CYAN}{Colors.BOLD}Required Python Modules:{Colors.ENDC}")
    modules = [
        ('fastapi', 'fastapi'),
        ('sqlalchemy', 'sqlalchemy'),
        ('pydantic', 'pydantic'),
        ('chromadb', 'chromadb'),
        ('markitdown', 'markitdown'),
        ('requests', 'requests'),
        ('reportlab', 'reportlab'),
        ('psycopg2-binary', 'psycopg2'),
        ('python-dotenv', 'dotenv'),
        ('openai', 'openai'),
        ('pydantic-ai', 'pydantic_ai'),
    ]

    for display_name, import_name in modules:
        all_good &= check_module(display_name, import_name)

    # Summary
    print(f"\n{Colors.BOLD}{'='*60}{Colors.ENDC}")
    if all_good:
        print(f"{Colors.GREEN}{Colors.BOLD}✓ All checks passed!{Colors.ENDC}")
        print(f"\nYour environment is configured correctly.")
        print(f"You can now run: {Colors.CYAN}python test_backend.py --clear{Colors.ENDC}")
    else:
        print(f"{Colors.RED}{Colors.BOLD}✗ Some checks failed!{Colors.ENDC}")
        print(f"\n{Colors.YELLOW}Action items:{Colors.ENDC}")
        print(f"1. Check your .env file and add missing variables")
        print(f"2. Install missing modules: pip install -r requirements.txt")
        print(f"3. Verify Supabase credentials are correct")

    print(f"{Colors.BOLD}{'='*60}{Colors.ENDC}\n")

    sys.exit(0 if all_good else 1)

if __name__ == "__main__":
    main()
