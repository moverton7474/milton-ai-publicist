"""
System Health Check
Comprehensive health monitoring for all system components
"""

import os
import sys
import asyncio
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime
import sqlite3

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from security.api_key_manager import APIKeyManager
from security.oauth_manager import OAuthManager
from security.secrets_manager import SecretsManager


class HealthChecker:
    """Comprehensive system health checker"""

    def __init__(self):
        """Initialize health checker"""
        self.checks = []
        self.results = {}

    async def check_all(self) -> Dict[str, Any]:
        """
        Run all health checks

        Returns:
            Health status dictionary
        """
        checks = [
            self.check_environment(),
            self.check_database(),
            await self.check_api_keys(),
            self.check_oauth(),
            self.check_secrets_backend(),
            self.check_filesystem(),
            self.check_dependencies()
        ]

        # Compile results
        all_healthy = all(check["healthy"] for check in checks)

        return {
            "timestamp": datetime.now().isoformat(),
            "overall_health": "healthy" if all_healthy else "degraded",
            "checks": checks,
            "summary": self._generate_summary(checks)
        }

    def check_environment(self) -> Dict[str, Any]:
        """Check environment configuration"""
        result = {
            "component": "environment",
            "healthy": True,
            "details": {},
            "issues": []
        }

        # Check Python version
        py_version = sys.version_info
        result["details"]["python_version"] = f"{py_version.major}.{py_version.minor}.{py_version.micro}"

        if py_version < (3, 11):
            result["healthy"] = False
            result["issues"].append("Python 3.11+ required")

        # Check environment variables
        required_vars = ["ANTHROPIC_API_KEY", "SECRET_KEY", "DATABASE_URL"]
        missing = []

        for var in required_vars:
            value = os.getenv(var)
            is_set = bool(value and value not in ["xxxxx", "sk-ant-xxxxx"])
            result["details"][var] = "configured" if is_set else "missing"

            if not is_set:
                missing.append(var)

        if missing:
            result["healthy"] = False
            result["issues"].extend([f"{var} not configured" for var in missing])

        # Check environment mode
        result["details"]["environment"] = os.getenv("ENVIRONMENT", "development")
        result["details"]["debug"] = os.getenv("DEBUG", "false")
        result["details"]["test_mode"] = os.getenv("TEST_MODE", "false")

        return result

    def check_database(self) -> Dict[str, Any]:
        """Check database health"""
        result = {
            "component": "database",
            "healthy": True,
            "details": {},
            "issues": []
        }

        db_url = os.getenv("DATABASE_URL", "")

        if "sqlite" in db_url:
            # Check SQLite database
            db_path = Path(__file__).parent.parent / "milton_publicist.db"

            if not db_path.exists():
                result["healthy"] = False
                result["issues"].append("Database file not found")
                return result

            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
                conn.close()

                result["details"]["type"] = "SQLite"
                result["details"]["path"] = str(db_path)
                result["details"]["tables_count"] = len(tables)
                result["details"]["tables"] = tables

                # Check for required tables
                required_tables = ["posts", "scheduled_posts", "publishing_results", "oauth_tokens"]
                missing_tables = [t for t in required_tables if t not in tables]

                if missing_tables:
                    result["healthy"] = False
                    result["issues"].extend([f"Missing table: {t}" for t in missing_tables])

            except Exception as e:
                result["healthy"] = False
                result["issues"].append(f"Database error: {str(e)}")

        elif "postgresql" in db_url:
            result["details"]["type"] = "PostgreSQL"
            result["details"]["configured"] = True
            # In production, would test actual connection

        return result

    async def check_api_keys(self) -> Dict[str, Any]:
        """Check API keys health"""
        result = {
            "component": "api_keys",
            "healthy": True,
            "details": {},
            "issues": []
        }

        try:
            manager = APIKeyManager()
            validation = await manager.validate_all_keys(test_connections=True)

            summary = validation["summary"]
            result["details"]["required_keys"] = f"{summary['required_configured']}/{summary['total_required']}"
            result["details"]["optional_keys"] = f"{summary['optional_configured']}/{summary['total_optional']}"

            # Check each key
            for key_name, data in validation["api_keys"].items():
                info = data["info"]
                val = data["validation"]

                result["details"][key_name] = {
                    "status": val["status"].value,
                    "required": info.get("required", False)
                }

                if info.get("required") and val["status"].value != "valid":
                    result["healthy"] = False
                    result["issues"].append(f"{info['name']}: {val['error'] or 'not configured'}")

        except Exception as e:
            result["healthy"] = False
            result["issues"].append(f"API key check failed: {str(e)}")

        return result

    def check_oauth(self) -> Dict[str, Any]:
        """Check OAuth configuration"""
        result = {
            "component": "oauth",
            "healthy": True,
            "details": {},
            "issues": []
        }

        try:
            manager = OAuthManager()

            # Check Clerk configuration
            clerk_config = manager.config.get("clerk_config", {})
            result["details"]["clerk_configured"] = clerk_config.get("configured", False)

            if not clerk_config.get("configured"):
                result["issues"].append("Clerk not configured (optional for content generation)")

            # Check platform connections
            platforms = manager.get_platform_status()
            result["details"]["platforms"] = platforms
            result["details"]["connected_count"] = sum(1 for status in platforms.values() if status)

            # Validate configuration
            is_valid, issues = manager.validate_configuration()
            result["details"]["configuration_valid"] = is_valid

            if not is_valid:
                result["issues"].extend(issues)
                # OAuth not being configured is OK for basic operation
                # result["healthy"] = False

        except Exception as e:
            result["healthy"] = False
            result["issues"].append(f"OAuth check failed: {str(e)}")

        return result

    def check_secrets_backend(self) -> Dict[str, Any]:
        """Check secrets management backend"""
        result = {
            "component": "secrets_management",
            "healthy": True,
            "details": {},
            "issues": []
        }

        try:
            manager = SecretsManager()
            health = manager.health_check()

            result["details"]["backend"] = health["backend"]
            result["details"]["backend_healthy"] = health["healthy"]

            if not health["healthy"]:
                result["healthy"] = False
                result["issues"].append(f"Secrets backend error: {health.get('error')}")

        except Exception as e:
            result["healthy"] = False
            result["issues"].append(f"Secrets check failed: {str(e)}")

        return result

    def check_filesystem(self) -> Dict[str, Any]:
        """Check filesystem permissions and directories"""
        result = {
            "component": "filesystem",
            "healthy": True,
            "details": {},
            "issues": []
        }

        base_path = Path(__file__).parent.parent

        # Check required directories
        required_dirs = ["data", "logs", "database", "security", "dashboard", "module_ii", "module_iii"]

        for dir_name in required_dirs:
            dir_path = base_path / dir_name
            exists = dir_path.exists()
            result["details"][dir_name] = "exists" if exists else "missing"

            if not exists:
                result["healthy"] = False
                result["issues"].append(f"Missing directory: {dir_name}")

        # Check write permissions
        try:
            test_file = base_path / "logs" / ".health_check_test"
            test_file.parent.mkdir(exist_ok=True)
            test_file.write_text("test")
            test_file.unlink()
            result["details"]["write_permission"] = True
        except Exception as e:
            result["healthy"] = False
            result["details"]["write_permission"] = False
            result["issues"].append(f"No write permission: {str(e)}")

        return result

    def check_dependencies(self) -> Dict[str, Any]:
        """Check Python dependencies"""
        result = {
            "component": "dependencies",
            "healthy": True,
            "details": {},
            "issues": []
        }

        required_packages = {
            "anthropic": "Anthropic Claude",
            "fastapi": "FastAPI web framework",
            "uvicorn": "ASGI server",
            "pydantic": "Data validation",
            "aiosqlite": "Async SQLite",
            "jinja2": "Template engine",
            "cryptography": "Encryption"
        }

        missing = []

        for package, name in required_packages.items():
            try:
                __import__(package)
                result["details"][package] = "installed"
            except ImportError:
                result["details"][package] = "missing"
                missing.append(name)

        if missing:
            result["healthy"] = False
            result["issues"].extend([f"Missing package: {pkg}" for pkg in missing])

        return result

    def _generate_summary(self, checks: List[Dict]) -> Dict[str, Any]:
        """Generate summary of all checks"""
        total = len(checks)
        healthy = sum(1 for check in checks if check["healthy"])
        all_issues = []

        for check in checks:
            all_issues.extend(check.get("issues", []))

        return {
            "total_checks": total,
            "passed": healthy,
            "failed": total - healthy,
            "pass_rate": f"{(healthy/total)*100:.1f}%",
            "critical_issues": len([i for i in all_issues if "required" in i.lower() or "missing" in i.lower()]),
            "warnings": len(all_issues) - len([i for i in all_issues if "required" in i.lower()])
        }


async def run_health_check() -> Dict[str, Any]:
    """Run complete health check"""
    checker = HealthChecker()
    return await checker.check_all()


async def print_health_report():
    """Print formatted health report"""
    print("=" * 70)
    print("MILTON AI PUBLICIST - SYSTEM HEALTH CHECK")
    print("=" * 70)
    print()

    health = await run_health_check()

    # Overall status
    status = health["overall_health"]
    status_icon = "[OK]" if status == "healthy" else "[WARNING]"
    print(f"Overall Health: {status_icon} {status.upper()}")
    print(f"Timestamp: {health['timestamp']}")
    print()

    # Summary
    summary = health["summary"]
    print("Summary:")
    print(f"  Checks Passed: {summary['passed']}/{summary['total_checks']} ({summary['pass_rate']})")
    print(f"  Critical Issues: {summary['critical_issues']}")
    print(f"  Warnings: {summary['warnings']}")
    print()

    # Individual checks
    print("Component Status:")
    for check in health["checks"]:
        icon = "[OK]" if check["healthy"] else "[FAIL]"
        component = check["component"].replace("_", " ").title()
        print(f"  {icon} {component}")

        # Show issues
        if check["issues"]:
            for issue in check["issues"]:
                print(f"      - {issue}")

    print()
    print("=" * 70)

    # Return exit code
    return 0 if status == "healthy" else 1


if __name__ == "__main__":
    exit_code = asyncio.run(print_health_report())
    sys.exit(exit_code)
