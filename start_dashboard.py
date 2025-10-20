"""
Milton AI Publicist - Dashboard Startup Script
Launches the approval dashboard with automatic dependency checking
"""

import os
import sys
import subprocess
import webbrowser
from pathlib import Path

def check_dependencies():
    """Check if all required packages are installed"""
    required_packages = {
        'fastapi': 'fastapi',
        'uvicorn': 'uvicorn',
        'jinja2': 'jinja2',
        'aiofiles': 'aiofiles',
        'anthropic': 'anthropic',
        'clerk_backend_api': 'clerk-backend-api',
        'aiohttp': 'aiohttp',
        'dotenv': 'python-dotenv'
    }

    missing = []

    for package, pip_name in required_packages.items():
        try:
            __import__(package)
        except ImportError:
            missing.append(pip_name)

    return missing

def check_env_file():
    """Check if .env file exists and has required keys"""
    env_path = Path(__file__).parent / '.env'

    if not env_path.exists():
        return False, [".env file not found"]

    required_keys = [
        'ANTHROPIC_API_KEY',
        'CLERK_SECRET_KEY',
        'MILTON_USER_ID'
    ]

    missing_keys = []

    with open(env_path, 'r') as f:
        env_content = f.read()
        for key in required_keys:
            if key not in env_content or f'{key}=' not in env_content:
                missing_keys.append(key)

    return len(missing_keys) == 0, missing_keys

def main():
    print("="*70)
    print("MILTON AI PUBLICIST - DASHBOARD STARTUP")
    print("="*70)
    print()

    # Check dependencies
    print("[INFO] Checking dependencies...")
    missing_packages = check_dependencies()

    if missing_packages:
        print("[ERROR] Missing required packages:")
        for package in missing_packages:
            print(f"  - {package}")
        print()
        print("Install missing packages with:")
        print(f"  pip install {' '.join(missing_packages)}")
        return 1

    print("[OK] All dependencies installed")
    print()

    # Check .env file
    print("[INFO] Checking configuration...")
    env_ok, missing_keys = check_env_file()

    if not env_ok:
        print("[ERROR] Configuration issues:")
        for key in missing_keys:
            print(f"  - {key}")
        print()
        print("Please ensure .env file exists and contains all required keys")
        return 1

    print("[OK] Configuration valid")
    print()

    # Check OAuth status
    print("[INFO] OAuth Status:")
    try:
        from dotenv import load_dotenv
        from module_iii import ClerkSocialAuth

        load_dotenv()
        auth = ClerkSocialAuth()
        connections = auth.verify_all_connections()

        for platform, connected in connections.items():
            status = "[CONNECTED]" if connected else "[NOT CONNECTED]"
            print(f"  {status} {platform.capitalize()}")

        if not any(connections.values()):
            print()
            print("[WARN] No social media accounts connected yet")
            print("       Publishing features will be limited until OAuth is configured")
    except Exception as e:
        print(f"  [WARN] Could not check OAuth status: {e}")

    print()
    print("="*70)
    print("STARTING DASHBOARD SERVER")
    print("="*70)
    print()
    print("Dashboard will be available at: http://localhost:8080")
    print()
    print("Features:")
    print("  - Generate content in Milton's authentic voice")
    print("  - Preview and edit posts before publishing")
    print("  - Publish to LinkedIn (once OAuth connected)")
    print("  - View publishing history")
    print()
    print("Press CTRL+C to stop the server")
    print()
    print("="*70)
    print()

    # Wait a moment then open browser
    import time
    time.sleep(2)

    print("[INFO] Opening browser...")
    webbrowser.open('http://localhost:8080')

    # Start the dashboard
    dashboard_path = Path(__file__).parent / 'dashboard' / 'app.py'

    try:
        subprocess.run([
            sys.executable,
            str(dashboard_path)
        ])
    except KeyboardInterrupt:
        print()
        print("[INFO] Shutting down dashboard...")
        print("[OK] Dashboard stopped")
        return 0

if __name__ == "__main__":
    sys.exit(main())
