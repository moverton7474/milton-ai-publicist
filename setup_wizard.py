"""
Milton AI Publicist - Interactive Setup Wizard
Guides users through first-time configuration
"""

import os
import sys
import asyncio
from pathlib import Path
from typing import Optional
import getpass

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from security.api_key_manager import APIKeyManager
from security.oauth_manager import OAuthManager
from database.migrations import MigrationManager
from monitoring.health_check import HealthChecker


class SetupWizard:
    """Interactive setup wizard"""

    def __init__(self):
        """Initialize wizard"""
        self.env_path = Path(__file__).parent / ".env"
        self.env_vars = {}
        self.steps_completed = []

    def print_header(self, title: str):
        """Print formatted header"""
        print()
        print("=" * 70)
        print(f"  {title}")
        print("=" * 70)
        print()

    def print_step(self, step: int, total: int, title: str):
        """Print step header"""
        print()
        print(f"[Step {step}/{total}] {title}")
        print("-" * 70)

    def get_input(self, prompt: str, default: Optional[str] = None, secret: bool = False) -> str:
        """Get user input with optional default"""
        if default:
            full_prompt = f"{prompt} [{default}]: "
        else:
            full_prompt = f"{prompt}: "

        if secret:
            value = getpass.getpass(full_prompt)
        else:
            value = input(full_prompt)

        return value.strip() if value.strip() else default

    def confirm(self, prompt: str, default: bool = True) -> bool:
        """Get yes/no confirmation"""
        default_str = "Y/n" if default else "y/N"
        response = input(f"{prompt} [{default_str}]: ").strip().lower()

        if not response:
            return default

        return response in ['y', 'yes']

    async def run(self):
        """Run the complete setup wizard"""
        self.print_header("MILTON AI PUBLICIST - SETUP WIZARD")

        print("Welcome! This wizard will help you configure Milton AI Publicist.")
        print("The setup process takes about 10-15 minutes.")
        print()

        if not self.confirm("Ready to begin?"):
            print("\nSetup cancelled. Run 'python setup_wizard.py' when ready.")
            return 1

        # Step 1: Environment check
        await self.step_environment_check()

        # Step 2: API keys
        await self.step_api_keys()

        # Step 3: Database
        await self.step_database()

        # Step 4: OAuth (optional)
        await self.step_oauth()

        # Step 5: Final verification
        await self.step_verification()

        # Complete
        self.print_completion()

        return 0

    async def step_environment_check(self):
        """Step 1: Check environment"""
        self.print_step(1, 5, "Environment Check")

        print("Checking your system...")
        print()

        # Check Python version
        py_version = sys.version_info
        print(f"Python Version: {py_version.major}.{py_version.minor}.{py_version.micro}")

        if py_version < (3, 11):
            print("[ERROR] Python 3.11 or higher is required!")
            print("Please upgrade Python and try again.")
            sys.exit(1)
        else:
            print("[OK] Python version is compatible")

        # Check virtual environment
        in_venv = sys.prefix != sys.base_prefix
        print(f"Virtual Environment: {'Active' if in_venv else 'Not active'}")

        if not in_venv:
            print("[WARNING] Not running in virtual environment")
            print("Consider activating venv: venv\\Scripts\\activate")
        else:
            print("[OK] Virtual environment active")

        # Check .env file
        if self.env_path.exists():
            print("[OK] .env file exists")
            self._load_env()
        else:
            print("[INFO] Creating .env file from template...")
            self._create_env_from_template()
            print("[OK] .env file created")

        self.steps_completed.append("environment_check")

        input("\nPress Enter to continue...")

    async def step_api_keys(self):
        """Step 2: Configure API keys"""
        self.print_step(2, 5, "API Key Configuration")

        print("Let's configure your API keys.")
        print()

        # Anthropic API (required)
        print("1. ANTHROPIC API KEY (REQUIRED)")
        print("   This is needed for content generation using Claude AI.")
        print("   Get your key at: https://console.anthropic.com/")
        print()

        current_anthropic = os.getenv("ANTHROPIC_API_KEY", "")
        if current_anthropic and current_anthropic != "sk-ant-xxxxx":
            print(f"   Current key: {current_anthropic[:15]}...")

            if self.confirm("   Keep existing key?"):
                self.env_vars["ANTHROPIC_API_KEY"] = current_anthropic
            else:
                new_key = self.get_input("   Enter new Anthropic API key", secret=True)
                self.env_vars["ANTHROPIC_API_KEY"] = new_key
        else:
            print("   No key configured yet.")
            anthropic_key = self.get_input("   Enter Anthropic API key (or press Enter to skip)", secret=True)

            if anthropic_key:
                self.env_vars["ANTHROPIC_API_KEY"] = anthropic_key
                print("   [OK] API key saved")
            else:
                print("   [SKIP] You can add this later in .env file")

        print()

        # OpenAI API (optional)
        print("2. OPENAI API KEY (Optional)")
        print("   Needed for voice transcription features.")
        print()

        if self.confirm("   Configure OpenAI API key?", default=False):
            openai_key = self.get_input("   Enter OpenAI API key", secret=True)
            if openai_key:
                self.env_vars["OPENAI_API_KEY"] = openai_key
                print("   [OK] API key saved")
        else:
            print("   [SKIP] Skipping OpenAI configuration")

        print()

        # Save API keys to .env
        self._update_env_file()

        # Validate API keys
        if "ANTHROPIC_API_KEY" in self.env_vars:
            print("\nValidating Anthropic API key...")
            manager = APIKeyManager()
            result = await manager.validate_key("ANTHROPIC_API_KEY", test_connection=True)

            if result["status"].value == "valid":
                print("[OK] API key is valid and working!")
            else:
                print(f"[WARNING] API key validation: {result['error']}")
                print("You can update the key in .env file later.")

        self.steps_completed.append("api_keys")

        input("\nPress Enter to continue...")

    async def step_database(self):
        """Step 3: Initialize database"""
        self.print_step(3, 5, "Database Setup")

        print("Setting up the database...")
        print()

        # Check if database exists
        db_path = Path(__file__).parent / "milton_publicist.db"

        if db_path.exists():
            print(f"[OK] Database already exists: {db_path}")
            print()

            if self.confirm("Run database migrations?"):
                print("\nRunning migrations...")
                manager = MigrationManager()
                status = manager.status()

                print(f"Current version: {status['current_version']}")
                print(f"Pending migrations: {status['pending_count']}")

                if status['pending_count'] > 0:
                    applied = manager.migrate_up()
                    print(f"[OK] Applied {len(applied)} migration(s)")
                else:
                    print("[OK] Database is up to date")
        else:
            print(f"[INFO] Creating new database: {db_path}")
            print()

            # Initialize database
            from database.database_manager import DatabaseManager
            db = DatabaseManager()

            print("[OK] Database created")
            print()

            # Run migrations
            print("Running initial migrations...")
            manager = MigrationManager()
            applied = manager.migrate_up()
            print(f"[OK] Applied {len(applied)} migration(s)")

        self.steps_completed.append("database")

        input("\nPress Enter to continue...")

    async def step_oauth(self):
        """Step 4: OAuth configuration (optional)"""
        self.print_step(4, 5, "OAuth Setup (Optional)")

        print("OAuth allows you to publish directly to social media platforms.")
        print("This step is optional - you can configure it later.")
        print()

        if not self.confirm("Configure OAuth now?", default=False):
            print("[SKIP] Skipping OAuth configuration")
            print("You can configure OAuth later using the dashboard.")
            self.steps_completed.append("oauth_skipped")
            input("\nPress Enter to continue...")
            return

        print()
        print("To configure OAuth, you'll need:")
        print("  1. Clerk account (https://clerk.com)")
        print("  2. LinkedIn Developer account (for LinkedIn publishing)")
        print()
        print("For detailed setup instructions, see:")
        print("  CLERK_SETUP_NEXT_STEPS.md")
        print()

        if self.confirm("Do you have Clerk credentials?", default=False):
            print()
            clerk_key = self.get_input("Enter Clerk Secret Key", secret=True)
            user_id = self.get_input("Enter Milton User ID")

            if clerk_key and user_id:
                self.env_vars["CLERK_SECRET_KEY"] = clerk_key
                self.env_vars["MILTON_USER_ID"] = user_id

                # Save to OAuth manager
                manager = OAuthManager()
                manager.configure_clerk(clerk_key, user_id)

                print("[OK] Clerk configuration saved")
                self.steps_completed.append("oauth_configured")
            else:
                print("[WARNING] Incomplete credentials - skipping OAuth")
                self.steps_completed.append("oauth_partial")
        else:
            print()
            print("OAuth Setup Instructions:")
            print("  1. Visit: https://dashboard.clerk.com")
            print("  2. Create account and application")
            print("  3. Configure LinkedIn social connection")
            print("  4. Copy Secret Key and User ID")
            print("  5. Re-run this wizard or update .env file")
            self.steps_completed.append("oauth_skipped")

        # Save to .env
        if "CLERK_SECRET_KEY" in self.env_vars:
            self._update_env_file()

        input("\nPress Enter to continue...")

    async def step_verification(self):
        """Step 5: Final verification"""
        self.print_step(5, 5, "Final Verification")

        print("Running final system health check...")
        print()

        checker = HealthChecker()
        health = await checker.check_all()

        # Show results
        passed = sum(1 for check in health["checks"] if check["healthy"])
        total = len(health["checks"])

        print(f"Health Checks: {passed}/{total} passed")
        print()

        for check in health["checks"]:
            status = "[OK]" if check["healthy"] else "[WARN]"
            component = check["component"].replace("_", " ").title()
            print(f"  {status} {component}")

        print()

        if health["overall_health"] == "healthy":
            print("[OK] System is healthy and ready to use!")
        else:
            print("[WARNING] System has some warnings (see above)")
            print("Most warnings are for optional features.")

        self.steps_completed.append("verification")

        input("\nPress Enter to see setup summary...")

    def print_completion(self):
        """Print completion message"""
        self.print_header("SETUP COMPLETE!")

        print("Milton AI Publicist has been configured successfully!")
        print()

        print("Setup Summary:")
        for step in self.steps_completed:
            print(f"  [OK] {step.replace('_', ' ').title()}")

        print()
        print("Next Steps:")
        print()

        print("1. Start the dashboard:")
        print("   python start_dashboard.py")
        print()

        print("2. Open your browser:")
        print("   http://localhost:8080")
        print()

        print("3. Generate your first post:")
        print("   - Select voice type")
        print("   - Enter context")
        print("   - Click 'Generate Content'")
        print()

        if "oauth_configured" in self.steps_completed:
            print("4. Connect LinkedIn (optional):")
            print("   - Follow instructions in dashboard")
            print("   - Click 'Connect LinkedIn'")
            print()

        print("=" * 70)
        print()
        print("For help and documentation, see:")
        print("  - START_HERE.md")
        print("  - PHASE_3_READY.md")
        print("  - http://localhost:8080/docs (API docs, when running)")
        print()

        print("Let's Go Owls! 🦉")
        print()

    def _load_env(self):
        """Load existing .env file"""
        with open(self.env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

    def _create_env_from_template(self):
        """Create .env from template"""
        template_path = Path(__file__).parent / ".env.template"

        if template_path.exists():
            with open(template_path, 'r') as src:
                with open(self.env_path, 'w') as dst:
                    dst.write(src.read())

    def _update_env_file(self):
        """Update .env file with new values"""
        if not self.env_path.exists():
            self._create_env_from_template()

        # Read existing content
        with open(self.env_path, 'r') as f:
            lines = f.readlines()

        # Update lines
        updated_lines = []
        keys_updated = set()

        for line in lines:
            updated = False
            for key, value in self.env_vars.items():
                if line.startswith(f"{key}="):
                    updated_lines.append(f"{key}={value}\n")
                    keys_updated.add(key)
                    updated = True
                    break

            if not updated:
                updated_lines.append(line)

        # Add new keys
        for key, value in self.env_vars.items():
            if key not in keys_updated:
                updated_lines.append(f"{key}={value}\n")

        # Write back
        with open(self.env_path, 'w') as f:
            f.writelines(updated_lines)


async def main():
    """Main entry point"""
    wizard = SetupWizard()

    try:
        exit_code = await wizard.run()
        return exit_code
    except KeyboardInterrupt:
        print("\n\nSetup cancelled by user.")
        return 1
    except Exception as e:
        print(f"\n\nError during setup: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
