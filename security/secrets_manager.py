"""
Production Secrets Manager
Supports HashiCorp Vault and AWS Secrets Manager for production deployments
"""

import os
import json
from typing import Optional, Dict, Any
from enum import Enum
from dotenv import load_dotenv

load_dotenv()


class SecretsBackend(Enum):
    """Supported secrets management backends"""
    LOCAL = "local"
    VAULT = "vault"
    AWS = "aws"


class SecretsManager:
    """
    Unified interface for secrets management across different backends
    """

    def __init__(self, backend: Optional[str] = None):
        """
        Initialize secrets manager

        Args:
            backend: Backend type (local, vault, aws). Auto-detected if None.
        """
        if backend is None:
            backend = os.getenv("CREDENTIAL_STORAGE", "local")

        self.backend = SecretsBackend(backend)
        self._client = None
        self._initialize_backend()

    def _initialize_backend(self):
        """Initialize the configured backend"""
        if self.backend == SecretsBackend.VAULT:
            self._initialize_vault()
        elif self.backend == SecretsBackend.AWS:
            self._initialize_aws()
        elif self.backend == SecretsBackend.LOCAL:
            self._initialize_local()

    def _initialize_local(self):
        """Initialize local credential storage"""
        try:
            from .credential_manager import CredentialManager
            self._client = CredentialManager()
        except ImportError:
            print("Warning: Could not import CredentialManager")
            self._client = None

    def _initialize_vault(self):
        """Initialize HashiCorp Vault client"""
        try:
            import hvac

            vault_addr = os.getenv("VAULT_ADDR", "http://localhost:8200")
            vault_token = os.getenv("VAULT_TOKEN")
            vault_namespace = os.getenv("VAULT_NAMESPACE", "milton-publicist")

            if not vault_token:
                raise ValueError("VAULT_TOKEN not found in environment")

            self._client = hvac.Client(
                url=vault_addr,
                token=vault_token,
                namespace=vault_namespace
            )

            # Verify connection
            if not self._client.is_authenticated():
                raise ConnectionError("Failed to authenticate with Vault")

        except ImportError:
            raise ImportError(
                "hvac package required for Vault backend. "
                "Install with: pip install hvac"
            )

    def _initialize_aws(self):
        """Initialize AWS Secrets Manager client"""
        try:
            import boto3

            aws_region = os.getenv("AWS_REGION", "us-east-1")
            aws_prefix = os.getenv("AWS_SECRETS_PREFIX", "milton-publicist/")

            self._client = boto3.client(
                "secretsmanager",
                region_name=aws_region
            )
            self._aws_prefix = aws_prefix

        except ImportError:
            raise ImportError(
                "boto3 package required for AWS backend. "
                "Install with: pip install boto3"
            )

    def get_secret(self, key: str) -> Optional[str]:
        """
        Get a secret value

        Args:
            key: Secret key

        Returns:
            Secret value or None
        """
        if self.backend == SecretsBackend.LOCAL:
            return self._get_local_secret(key)
        elif self.backend == SecretsBackend.VAULT:
            return self._get_vault_secret(key)
        elif self.backend == SecretsBackend.AWS:
            return self._get_aws_secret(key)

    def set_secret(self, key: str, value: str) -> bool:
        """
        Set a secret value

        Args:
            key: Secret key
            value: Secret value

        Returns:
            True if successful
        """
        if self.backend == SecretsBackend.LOCAL:
            return self._set_local_secret(key, value)
        elif self.backend == SecretsBackend.VAULT:
            return self._set_vault_secret(key, value)
        elif self.backend == SecretsBackend.AWS:
            return self._set_aws_secret(key, value)

    def delete_secret(self, key: str) -> bool:
        """
        Delete a secret

        Args:
            key: Secret key

        Returns:
            True if successful
        """
        if self.backend == SecretsBackend.LOCAL:
            return self._delete_local_secret(key)
        elif self.backend == SecretsBackend.VAULT:
            return self._delete_vault_secret(key)
        elif self.backend == SecretsBackend.AWS:
            return self._delete_aws_secret(key)

    def list_secrets(self) -> list:
        """
        List all secret keys

        Returns:
            List of secret keys
        """
        if self.backend == SecretsBackend.LOCAL:
            return self._list_local_secrets()
        elif self.backend == SecretsBackend.VAULT:
            return self._list_vault_secrets()
        elif self.backend == SecretsBackend.AWS:
            return self._list_aws_secrets()

    # Local backend methods
    def _get_local_secret(self, key: str) -> Optional[str]:
        """Get secret from local storage"""
        if self._client:
            return self._client.get_credential(key)
        return os.getenv(key)

    def _set_local_secret(self, key: str, value: str) -> bool:
        """Set secret in local storage"""
        if self._client:
            self._client.save_credential(key, value)
            return True
        return False

    def _delete_local_secret(self, key: str) -> bool:
        """Delete secret from local storage"""
        if self._client:
            return self._client.delete_credential(key)
        return False

    def _list_local_secrets(self) -> list:
        """List local secrets"""
        if self._client:
            return self._client.list_credentials()
        return []

    # Vault backend methods
    def _get_vault_secret(self, key: str) -> Optional[str]:
        """Get secret from Vault"""
        try:
            secret = self._client.secrets.kv.v2.read_secret_version(
                path=key,
                mount_point="secret"
            )
            return secret["data"]["data"]["value"]
        except Exception as e:
            print(f"Error reading from Vault: {e}")
            return None

    def _set_vault_secret(self, key: str, value: str) -> bool:
        """Set secret in Vault"""
        try:
            self._client.secrets.kv.v2.create_or_update_secret(
                path=key,
                secret={"value": value},
                mount_point="secret"
            )
            return True
        except Exception as e:
            print(f"Error writing to Vault: {e}")
            return False

    def _delete_vault_secret(self, key: str) -> bool:
        """Delete secret from Vault"""
        try:
            self._client.secrets.kv.v2.delete_metadata_and_all_versions(
                path=key,
                mount_point="secret"
            )
            return True
        except Exception as e:
            print(f"Error deleting from Vault: {e}")
            return False

    def _list_vault_secrets(self) -> list:
        """List Vault secrets"""
        try:
            secrets = self._client.secrets.kv.v2.list_secrets(
                path="",
                mount_point="secret"
            )
            return secrets["data"]["keys"]
        except Exception as e:
            print(f"Error listing Vault secrets: {e}")
            return []

    # AWS backend methods
    def _get_aws_secret(self, key: str) -> Optional[str]:
        """Get secret from AWS Secrets Manager"""
        try:
            response = self._client.get_secret_value(
                SecretId=f"{self._aws_prefix}{key}"
            )
            return response["SecretString"]
        except self._client.exceptions.ResourceNotFoundException:
            return None
        except Exception as e:
            print(f"Error reading from AWS: {e}")
            return None

    def _set_aws_secret(self, key: str, value: str) -> bool:
        """Set secret in AWS Secrets Manager"""
        try:
            secret_id = f"{self._aws_prefix}{key}"

            # Try to create new secret
            try:
                self._client.create_secret(
                    Name=secret_id,
                    SecretString=value
                )
            except self._client.exceptions.ResourceExistsException:
                # Update existing secret
                self._client.update_secret(
                    SecretId=secret_id,
                    SecretString=value
                )

            return True
        except Exception as e:
            print(f"Error writing to AWS: {e}")
            return False

    def _delete_aws_secret(self, key: str) -> bool:
        """Delete secret from AWS Secrets Manager"""
        try:
            self._client.delete_secret(
                SecretId=f"{self._aws_prefix}{key}",
                ForceDeleteWithoutRecovery=True
            )
            return True
        except Exception as e:
            print(f"Error deleting from AWS: {e}")
            return False

    def _list_aws_secrets(self) -> list:
        """List AWS secrets"""
        try:
            paginator = self._client.get_paginator('list_secrets')
            secrets = []

            for page in paginator.paginate():
                for secret in page['SecretList']:
                    name = secret['Name']
                    if name.startswith(self._aws_prefix):
                        # Remove prefix
                        secrets.append(name[len(self._aws_prefix):])

            return secrets
        except Exception as e:
            print(f"Error listing AWS secrets: {e}")
            return []

    def migrate_secrets(self, target_backend: str, keys: Optional[list] = None):
        """
        Migrate secrets to a different backend

        Args:
            target_backend: Target backend (local, vault, aws)
            keys: List of keys to migrate (None = all)
        """
        target = SecretsManager(backend=target_backend)

        if keys is None:
            keys = self.list_secrets()

        migrated = 0
        failed = 0

        for key in keys:
            try:
                value = self.get_secret(key)
                if value:
                    if target.set_secret(key, value):
                        migrated += 1
                    else:
                        failed += 1
            except Exception as e:
                print(f"Failed to migrate {key}: {e}")
                failed += 1

        return {
            "migrated": migrated,
            "failed": failed,
            "total": len(keys)
        }

    def health_check(self) -> Dict[str, Any]:
        """
        Check health of secrets backend

        Returns:
            Health status dictionary
        """
        health = {
            "backend": self.backend.value,
            "healthy": False,
            "error": None
        }

        try:
            if self.backend == SecretsBackend.LOCAL:
                health["healthy"] = self._client is not None

            elif self.backend == SecretsBackend.VAULT:
                health["healthy"] = self._client.is_authenticated()

            elif self.backend == SecretsBackend.AWS:
                # Try to list secrets as health check
                self._client.list_secrets(MaxResults=1)
                health["healthy"] = True

        except Exception as e:
            health["error"] = str(e)

        return health


# Convenience functions

_manager_instance = None


def get_secrets_manager() -> SecretsManager:
    """Get singleton secrets manager instance"""
    global _manager_instance
    if _manager_instance is None:
        _manager_instance = SecretsManager()
    return _manager_instance


def get_secret(key: str) -> Optional[str]:
    """Get a secret value"""
    manager = get_secrets_manager()
    return manager.get_secret(key)


def set_secret(key: str, value: str) -> bool:
    """Set a secret value"""
    manager = get_secrets_manager()
    return manager.set_secret(key, value)


if __name__ == "__main__":
    print("=" * 60)
    print("SECRETS MANAGER")
    print("=" * 60)
    print()

    manager = SecretsManager()

    print(f"Backend: {manager.backend.value}")
    print()

    # Health check
    health = manager.health_check()
    print(f"Health: {'[OK]' if health['healthy'] else '[ERROR]'}")
    if health['error']:
        print(f"Error: {health['error']}")

    print()

    # List secrets
    secrets = manager.list_secrets()
    print(f"Secrets stored: {len(secrets)}")
    for secret_key in secrets:
        print(f"  - {secret_key}")

    print()
    print("=" * 60)
