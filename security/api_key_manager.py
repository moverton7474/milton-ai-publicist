"""
API Key Manager
Validates and manages API keys for external services
"""

import os
import re
from typing import Dict, Optional, List, Tuple
from enum import Enum
from dotenv import load_dotenv
import anthropic
import httpx

load_dotenv()


class KeyStatus(Enum):
    """API key status"""
    VALID = "valid"
    INVALID = "invalid"
    MISSING = "missing"
    EXPIRED = "expired"
    QUOTA_EXCEEDED = "quota_exceeded"
    UNKNOWN = "unknown"


class APIKeyManager:
    """
    Manages and validates API keys for external services
    """

    REQUIRED_KEYS = {
        "ANTHROPIC_API_KEY": {
            "name": "Anthropic (Claude)",
            "pattern": r"^sk-ant-api03-[\w\-]{95}$",
            "url": "https://console.anthropic.com/",
            "required": True,
            "testable": True
        },
        "OPENAI_API_KEY": {
            "name": "OpenAI",
            "pattern": r"^sk-[\w]{48}$",
            "url": "https://platform.openai.com/api-keys",
            "required": False,
            "testable": True
        },
        "HEYGEN_API_KEY": {
            "name": "HeyGen",
            "pattern": r"^[\w\-]{32,}$",
            "url": "https://app.heygen.com/settings/api-keys",
            "required": False,
            "testable": False
        },
        "CLERK_SECRET_KEY": {
            "name": "Clerk",
            "pattern": r"^sk_test_[\w]{40,}$",
            "url": "https://dashboard.clerk.com/",
            "required": False,
            "testable": True
        }
    }

    WEBHOOK_KEYS = {
        "ZAPIER_LINKEDIN_WEBHOOK": {
            "name": "Zapier LinkedIn",
            "pattern": r"^https://hooks\.zapier\.com/hooks/catch/\d+/[\w]+/$",
            "required": False
        },
        "ZAPIER_TWITTER_WEBHOOK": {
            "name": "Zapier Twitter",
            "pattern": r"^https://hooks\.zapier\.com/hooks/catch/\d+/[\w]+/$",
            "required": False
        },
        "ZAPIER_INSTAGRAM_WEBHOOK": {
            "name": "Zapier Instagram",
            "pattern": r"^https://hooks\.zapier\.com/hooks/catch/\d+/[\w]+/$",
            "required": False
        }
    }

    def __init__(self):
        """Initialize API key manager"""
        self.keys_cache = {}
        self.validation_cache = {}

    def get_key(self, key_name: str) -> Optional[str]:
        """
        Get API key from environment

        Args:
            key_name: Environment variable name

        Returns:
            API key or None
        """
        return os.getenv(key_name)

    def validate_key_format(self, key_name: str, key_value: str) -> bool:
        """
        Validate API key format using regex pattern

        Args:
            key_name: Key identifier
            key_value: Key value to validate

        Returns:
            True if format is valid
        """
        key_info = self.REQUIRED_KEYS.get(key_name) or self.WEBHOOK_KEYS.get(key_name)
        if not key_info:
            return True  # Unknown keys pass validation

        pattern = key_info.get("pattern")
        if not pattern:
            return True

        return bool(re.match(pattern, key_value))

    async def test_anthropic_key(self, api_key: str) -> Tuple[KeyStatus, Optional[str]]:
        """
        Test Anthropic API key by making a minimal API call

        Args:
            api_key: Anthropic API key

        Returns:
            Tuple of (status, error_message)
        """
        try:
            client = anthropic.Anthropic(api_key=api_key)

            # Make minimal API call
            response = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=10,
                messages=[{"role": "user", "content": "Hi"}]
            )

            return KeyStatus.VALID, None

        except anthropic.AuthenticationError:
            return KeyStatus.INVALID, "Invalid API key"
        except anthropic.PermissionDeniedError:
            return KeyStatus.INVALID, "Permission denied"
        except anthropic.RateLimitError:
            return KeyStatus.QUOTA_EXCEEDED, "Rate limit exceeded"
        except Exception as e:
            return KeyStatus.UNKNOWN, str(e)

    async def test_openai_key(self, api_key: str) -> Tuple[KeyStatus, Optional[str]]:
        """
        Test OpenAI API key

        Args:
            api_key: OpenAI API key

        Returns:
            Tuple of (status, error_message)
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://api.openai.com/v1/models",
                    headers={"Authorization": f"Bearer {api_key}"},
                    timeout=10.0
                )

                if response.status_code == 200:
                    return KeyStatus.VALID, None
                elif response.status_code == 401:
                    return KeyStatus.INVALID, "Invalid API key"
                else:
                    return KeyStatus.UNKNOWN, f"HTTP {response.status_code}"

        except Exception as e:
            return KeyStatus.UNKNOWN, str(e)

    async def test_clerk_key(self, api_key: str) -> Tuple[KeyStatus, Optional[str]]:
        """
        Test Clerk API key

        Args:
            api_key: Clerk secret key

        Returns:
            Tuple of (status, error_message)
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://api.clerk.com/v1/users",
                    headers={"Authorization": f"Bearer {api_key}"},
                    timeout=10.0
                )

                if response.status_code == 200:
                    return KeyStatus.VALID, None
                elif response.status_code == 401:
                    return KeyStatus.INVALID, "Invalid API key"
                else:
                    return KeyStatus.UNKNOWN, f"HTTP {response.status_code}"

        except Exception as e:
            return KeyStatus.UNKNOWN, str(e)

    async def validate_key(self, key_name: str, test_connection: bool = True) -> Dict:
        """
        Validate an API key

        Args:
            key_name: Environment variable name
            test_connection: Whether to test actual API connection

        Returns:
            Validation result dictionary
        """
        result = {
            "key_name": key_name,
            "present": False,
            "format_valid": False,
            "connection_tested": False,
            "status": KeyStatus.MISSING,
            "error": None,
            "metadata": {}
        }

        # Check if key exists
        key_value = self.get_key(key_name)
        if not key_value or key_value in ["xxxxx", "sk-ant-xxxxx", "sk-xxxxx"]:
            result["status"] = KeyStatus.MISSING
            result["error"] = "API key not configured"
            return result

        result["present"] = True

        # Validate format
        result["format_valid"] = self.validate_key_format(key_name, key_value)
        if not result["format_valid"]:
            result["status"] = KeyStatus.INVALID
            result["error"] = "Invalid key format"
            return result

        # Test connection if requested
        if test_connection:
            key_info = self.REQUIRED_KEYS.get(key_name, {})
            if key_info.get("testable"):
                result["connection_tested"] = True

                if key_name == "ANTHROPIC_API_KEY":
                    status, error = await self.test_anthropic_key(key_value)
                    result["status"] = status
                    result["error"] = error
                elif key_name == "OPENAI_API_KEY":
                    status, error = await self.test_openai_key(key_value)
                    result["status"] = status
                    result["error"] = error
                elif key_name == "CLERK_SECRET_KEY":
                    status, error = await self.test_clerk_key(key_value)
                    result["status"] = status
                    result["error"] = error
            else:
                result["status"] = KeyStatus.VALID  # Assume valid if format is correct

        else:
            result["status"] = KeyStatus.VALID if result["format_valid"] else KeyStatus.INVALID

        return result

    async def validate_all_keys(self, test_connections: bool = False) -> Dict:
        """
        Validate all configured API keys

        Args:
            test_connections: Whether to test actual API connections

        Returns:
            Dictionary of validation results
        """
        results = {
            "api_keys": {},
            "webhooks": {},
            "summary": {
                "total_required": 0,
                "required_configured": 0,
                "total_optional": 0,
                "optional_configured": 0,
                "all_required_present": False
            }
        }

        # Validate API keys
        for key_name, key_info in self.REQUIRED_KEYS.items():
            validation = await self.validate_key(key_name, test_connections)
            results["api_keys"][key_name] = {
                "info": key_info,
                "validation": validation
            }

            if key_info.get("required"):
                results["summary"]["total_required"] += 1
                if validation["status"] == KeyStatus.VALID:
                    results["summary"]["required_configured"] += 1
            else:
                results["summary"]["total_optional"] += 1
                if validation["status"] == KeyStatus.VALID:
                    results["summary"]["optional_configured"] += 1

        # Validate webhooks
        for webhook_name, webhook_info in self.WEBHOOK_KEYS.items():
            webhook_url = self.get_key(webhook_name)
            is_configured = bool(webhook_url and webhook_url != "https://hooks.zapier.com/hooks/catch/XXXXX/YYYYY/")

            results["webhooks"][webhook_name] = {
                "info": webhook_info,
                "configured": is_configured,
                "url": webhook_url if is_configured else None
            }

        # Calculate summary
        results["summary"]["all_required_present"] = (
            results["summary"]["required_configured"] == results["summary"]["total_required"]
        )

        return results

    def get_setup_instructions(self, key_name: str) -> Dict:
        """
        Get setup instructions for an API key

        Args:
            key_name: Environment variable name

        Returns:
            Instructions dictionary
        """
        key_info = self.REQUIRED_KEYS.get(key_name, {})

        return {
            "key_name": key_name,
            "service_name": key_info.get("name", key_name),
            "url": key_info.get("url"),
            "required": key_info.get("required", False),
            "steps": self._get_key_steps(key_name)
        }

    def _get_key_steps(self, key_name: str) -> List[str]:
        """Get setup steps for a specific key"""
        steps = {
            "ANTHROPIC_API_KEY": [
                "Go to https://console.anthropic.com/",
                "Sign up or log in to your account",
                "Navigate to 'API Keys' section",
                "Click 'Create Key'",
                "Copy the key (starts with sk-ant-api03-)",
                "Add to .env file: ANTHROPIC_API_KEY=your-key-here"
            ],
            "OPENAI_API_KEY": [
                "Go to https://platform.openai.com/api-keys",
                "Sign up or log in",
                "Click '+ Create new secret key'",
                "Copy the key (starts with sk-)",
                "Add to .env file: OPENAI_API_KEY=your-key-here"
            ],
            "HEYGEN_API_KEY": [
                "Go to https://app.heygen.com/settings/api-keys",
                "Sign up or log in",
                "Generate new API key",
                "Copy the key",
                "Add to .env file: HEYGEN_API_KEY=your-key-here"
            ],
            "CLERK_SECRET_KEY": [
                "Go to https://dashboard.clerk.com/",
                "Create account or log in",
                "Create new application",
                "Go to 'API Keys' section",
                "Copy 'Secret Key' (starts with sk_test_)",
                "Add to .env file: CLERK_SECRET_KEY=your-key-here"
            ]
        }

        return steps.get(key_name, ["No specific instructions available"])

    def generate_health_report(self, validation_results: Dict) -> str:
        """
        Generate human-readable health report

        Args:
            validation_results: Results from validate_all_keys()

        Returns:
            Formatted report string
        """
        report = []
        report.append("=" * 60)
        report.append("API KEY HEALTH REPORT")
        report.append("=" * 60)
        report.append("")

        # Summary
        summary = validation_results["summary"]
        report.append("Summary:")
        report.append(f"  Required Keys: {summary['required_configured']}/{summary['total_required']}")
        report.append(f"  Optional Keys: {summary['optional_configured']}/{summary['total_optional']}")
        report.append(f"  Status: {'[OK]' if summary['all_required_present'] else '[INCOMPLETE]'}")
        report.append("")

        # API Keys
        report.append("API Keys:")
        for key_name, data in validation_results["api_keys"].items():
            info = data["info"]
            validation = data["validation"]

            status_icon = {
                KeyStatus.VALID: "[OK]",
                KeyStatus.INVALID: "[ERROR]",
                KeyStatus.MISSING: "[  ]",
                KeyStatus.QUOTA_EXCEEDED: "[WARN]",
                KeyStatus.UNKNOWN: "[?]"
            }.get(validation["status"], "[?]")

            required = "[REQUIRED]" if info.get("required") else "[OPTIONAL]"

            report.append(f"  {status_icon} {required} {info['name']}")

            if validation["error"]:
                report.append(f"      Error: {validation['error']}")

        report.append("")

        # Webhooks
        report.append("Webhooks:")
        for webhook_name, data in validation_results["webhooks"].items():
            info = data["info"]
            configured = data["configured"]

            status_icon = "[OK]" if configured else "[  ]"
            report.append(f"  {status_icon} {info['name']}")

        report.append("")
        report.append("=" * 60)

        return "\n".join(report)


# Convenience functions

async def validate_api_keys(test_connections: bool = False) -> Dict:
    """Validate all API keys"""
    manager = APIKeyManager()
    return await manager.validate_all_keys(test_connections)


async def print_health_report():
    """Print API key health report"""
    manager = APIKeyManager()
    results = await manager.validate_all_keys(test_connections=True)
    report = manager.generate_health_report(results)
    print(report)


if __name__ == "__main__":
    import asyncio

    async def main():
        print("Testing API Key Manager...")
        print()
        await print_health_report()

    asyncio.run(main())
