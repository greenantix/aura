import time
from functools import wraps
from typing import List, Callable, Any

class AuthorizationError(Exception):
    """Authorization-related error"""
    pass

class Permission:
    """Permission constants"""
    ANALYZE_CODE = "analyze_code"
    ACCESS_LLM = "access_llm"
    MODIFY_CONFIG = "modify_config"
    VIEW_METRICS = "view_metrics"
    ADMIN_ACCESS = "admin_access"

def require_permissions(permissions: List[str]):
    """Decorator to require specific permissions"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            service_context = kwargs.get('service_context')
            if not service_context:
                raise AuthorizationError("No service context provided")
            for permission in permissions:
                if not service_context.has_permission(permission):
                    raise AuthorizationError(f"Permission denied: {permission}")
            return await func(*args, **kwargs)
        return wrapper
    return decorator

class ServiceContext:
    """Context for authenticated service"""

    def __init__(self, service_id: str, permissions: List[str]):
        self.service_id = service_id
        self.permissions = permissions
        self.authenticated_at = time.time()

    def has_permission(self, permission: str) -> bool:
        """Check if service has specific permission"""
        return permission in self.permissions