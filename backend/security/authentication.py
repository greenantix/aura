import jwt
import time
import secrets
import hashlib
from typing import Dict, Optional, List
from dataclasses import dataclass

@dataclass
class ServiceCredentials:
    service_id: str
    api_key: str
    permissions: List[str]
    expires_at: Optional[float] = None

class AuthenticationError(Exception):
    """Authentication-related error"""
    pass

class AuthenticationManager:
    """Manage authentication for Aura services"""

    def __init__(self, secret_key: str):
        self.secret_key = secret_key
        self.service_registry: Dict[str, ServiceCredentials] = {}
        self.token_cache: Dict[str, Dict] = {}

    def register_service(self, service_id: str, permissions: List[str]) -> str:
        """Register a new service and generate API key"""
        api_key = secrets.token_urlsafe(32)
        credentials = ServiceCredentials(
            service_id=service_id,
            api_key=api_key,
            permissions=permissions
        )
        self.service_registry[service_id] = credentials
        return api_key

    def authenticate_service(self, service_id: str, api_key: str) -> bool:
        """Authenticate a service using API key"""
        credentials = self.service_registry.get(service_id)
        if not credentials:
            return False
        if not secrets.compare_digest(credentials.api_key, api_key):
            return False
        if credentials.expires_at and time.time() > credentials.expires_at:
            return False
        return True

    def generate_jwt_token(self, service_id: str, duration: int = 3600) -> str:
        """Generate JWT token for authenticated service"""
        credentials = self.service_registry.get(service_id)
        if not credentials:
            raise AuthenticationError("Service not registered")
        payload = {
            'service_id': service_id,
            'permissions': credentials.permissions,
            'iat': time.time(),
            'exp': time.time() + duration
        }
        token = jwt.encode(payload, self.secret_key, algorithm='HS256')
        self.token_cache[token] = payload
        return token

    def validate_jwt_token(self, token: str) -> Optional[Dict]:
        """Validate JWT token and return payload"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    def check_permission(self, service_id: str, permission: str) -> bool:
        """Check if service has specific permission"""
        credentials = self.service_registry.get(service_id)
        if not credentials:
            return False
        return permission in credentials.permissions