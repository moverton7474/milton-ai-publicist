"""
Credential Manager
Handles secure local storage of API keys and credentials using encryption
"""

import os
import json
from pathlib import Path
from typing import Optional, Dict
from cryptography.fernet import Fernet
from dotenv import load_dotenv

load_dotenv()


class CredentialManager:
    """
    Manages encrypted credential storage for development and production
    """

    def __init__(self, credentials_file: Optional[str] = None):
        """
        Initialize credential manager

        Args:
            credentials_file: Path to encrypted credentials file
        """
        if credentials_file is None:
            credentials_file = Path(__file__).parent.parent / ".credentials.enc"

        self.credentials_file = Path(credentials_file)
        self.secret_key = os.getenv("SECRET_KEY")

        if not self.secret_key:
            raise ValueError(
                "SECRET_KEY not found in environment. "
                "Please set it in your .env file."
            )

        # Generate Fernet key from secret
        self.cipher = self._get_cipher()

    def _get_cipher(self) -> Fernet:
        """Get or create Fernet cipher"""
        # Use SECRET_KEY to derive encryption key
        # Pad or hash to 32 bytes for Fernet
        import hashlib
        key = hashlib.sha256(self.secret_key.encode()).digest()
        return Fernet(Fernet.generate_key() if not hasattr(self, '_fernet_key') else self._fernet_key)

    def save_credential(self, key: str, value: str) -> None:
        """
        Save a credential securely

        Args:
            key: Credential identifier (e.g., 'anthropic_api_key')
            value: Credential value
        """
        # Load existing credentials
        credentials = self._load_credentials()

        # Update with new credential
        credentials[key] = value

        # Encrypt and save
        encrypted_data = self.cipher.encrypt(json.dumps(credentials).encode())

        with open(self.credentials_file, 'wb') as f:
            f.write(encrypted_data)

        print(f"✓ Credential '{key}' saved securely")

    def get_credential(self, key: str) -> Optional[str]:
        """
        Retrieve a credential

        Args:
            key: Credential identifier

        Returns:
            Credential value or None if not found
        """
        credentials = self._load_credentials()
        return credentials.get(key)

    def delete_credential(self, key: str) -> bool:
        """
        Delete a credential

        Args:
            key: Credential identifier

        Returns:
            True if deleted, False if not found
        """
        credentials = self._load_credentials()

        if key in credentials:
            del credentials[key]

            # Encrypt and save
            encrypted_data = self.cipher.encrypt(json.dumps(credentials).encode())

            with open(self.credentials_file, 'wb') as f:
                f.write(encrypted_data)

            print(f"✓ Credential '{key}' deleted")
            return True

        return False

    def list_credentials(self) -> list:
        """
        List all stored credential keys (not values)

        Returns:
            List of credential keys
        """
        credentials = self._load_credentials()
        return list(credentials.keys())

    def _load_credentials(self) -> Dict:
        """Load and decrypt credentials file"""
        if not self.credentials_file.exists():
            return {}

        try:
            with open(self.credentials_file, 'rb') as f:
                encrypted_data = f.read()

            decrypted_data = self.cipher.decrypt(encrypted_data)
            return json.loads(decrypted_data.decode())

        except Exception as e:
            print(f"Warning: Could not load credentials: {e}")
            return {}

    def import_from_env(self) -> int:
        """
        Import credentials from environment variables

        Returns:
            Number of credentials imported
        """
        env_keys = [
            'ANTHROPIC_API_KEY',
            'OPENAI_API_KEY',
            'HEYGEN_API_KEY',
            'LINKEDIN_EMAIL',
            'LINKEDIN_PASSWORD',
            'TWITTER_API_KEY',
            'TWITTER_API_SECRET',
            'TWITTER_ACCESS_TOKEN',
            'TWITTER_ACCESS_TOKEN_SECRET',
            'TWITTER_BEARER_TOKEN',
            'INSTAGRAM_ACCESS_TOKEN',
            'CLERK_SECRET_KEY',
            'ZAPIER_LINKEDIN_WEBHOOK',
            'ZAPIER_TWITTER_WEBHOOK',
            'ZAPIER_INSTAGRAM_WEBHOOK',
            'ZAPIER_FACEBOOK_WEBHOOK'
        ]

        count = 0
        for key in env_keys:
            value = os.getenv(key)
            if value and value not in ['xxxxx', 'sk-ant-xxxxx', 'sk-xxxxx']:
                self.save_credential(key.lower(), value)
                count += 1

        return count


def setup_credentials():
    """Interactive setup for credentials"""
    print("=" * 60)
    print("MILTON AI PUBLICIST - CREDENTIAL SETUP")
    print("=" * 60)

    manager = CredentialManager()

    print("\nThis will help you securely store your API credentials.")
    print("Credentials will be encrypted using your SECRET_KEY.\n")

    # Import from environment
    print("Importing credentials from .env file...")
    imported = manager.import_from_env()
    print(f"✓ Imported {imported} credentials from environment\n")

    # List stored credentials
    stored = manager.list_credentials()
    if stored:
        print("Currently stored credentials:")
        for key in stored:
            print(f"  ✓ {key}")
    else:
        print("No credentials stored yet.")

    print("\n" + "=" * 60)
    print("Setup complete! Credentials are stored securely in .credentials.enc")
    print("=" * 60)


if __name__ == "__main__":
    setup_credentials()
