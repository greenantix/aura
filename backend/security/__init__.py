"""
Aura Security Module
===================

Comprehensive security framework for authentication, authorization, 
encryption, and secure communication.

Components:
- Authentication: Service authentication with API keys and JWT
- Authorization: Permission-based access control
- Encryption: Data encryption for sensitive information
- Network Security: Secure HTTP client with TLS validation
- Input Validation: Security validation for all inputs
- Resource Management: Resource usage monitoring and limits
"""

from .authentication import AuthenticationManager, ServiceCredentials, AuthenticationError
from .authorization import (
    AuthorizationError, 
    Permission, 
    ServiceContext, 
    require_permissions
)
from .encryption import DataEncryption
from .network_security import SecureHTTPClient, SecurityError
from .input_validator import SecurityValidator, validate_code_input
from .resource_manager import ResourceManager

__all__ = [
    'AuthenticationManager',
    'ServiceCredentials', 
    'AuthenticationError',
    'AuthorizationError',
    'Permission',
    'ServiceContext',
    'require_permissions',
    'DataEncryption',
    'SecureHTTPClient',
    'SecurityError',
    'SecurityValidator',
    'validate_code_input',
    'ResourceManager'
]

# Default security configuration
DEFAULT_SECURITY_CONFIG = {
    'authentication': {
        'secret_key': 'aura-secure-key-change-in-production',
        'token_duration': 3600,  # 1 hour
        'api_key_length': 32
    },
    'authorization': {
        'default_permissions': [
            Permission.ANALYZE_CODE,
            Permission.VIEW_METRICS
        ],
        'admin_permissions': [
            Permission.ANALYZE_CODE,
            Permission.ACCESS_LLM,
            Permission.MODIFY_CONFIG,
            Permission.VIEW_METRICS,
            Permission.ADMIN_ACCESS
        ]
    },
    'encryption': {
        'algorithm': 'fernet',
        'key_derivation_iterations': 100000
    },
    'network': {
        'timeout': 30,
        'verify_ssl': True,
        'allowed_hosts': ['localhost', '127.0.0.1'],
        'max_response_size': 10 * 1024 * 1024  # 10MB
    },
    'resource_limits': {
        'max_memory_mb': 1024,
        'max_cpu_percent': 80,
        'max_file_size_mb': 50,
        'rate_limit_requests_per_minute': 60
    }
}


class SecurityManager:
    """Central security manager for Aura system"""
    
    def __init__(self, config: dict = None):
        """Initialize security manager with configuration"""
        self.config = config or DEFAULT_SECURITY_CONFIG
        
        # Initialize core security components
        self.auth_manager = AuthenticationManager(
            self.config['authentication']['secret_key']
        )
        
        self.encryption = DataEncryption(
            self.config['authentication']['secret_key']
        )
        
        self.http_client = SecureHTTPClient(
            self.config['network']
        )
        
        self.resource_manager = ResourceManager(
            self.config['resource_limits']
        )
        
        self.input_validator = SecurityValidator()
        
        # Register default services
        self._register_default_services()
    
    def _register_default_services(self):
        """Register default system services"""
        # Register core Aura services
        services = [
            ('aura_core', ['analyze_code', 'view_metrics']),
            ('aura_llm', ['access_llm', 'analyze_code']),
            ('aura_git', ['analyze_code', 'view_metrics']),
            ('aura_admin', [
                'analyze_code', 'access_llm', 'modify_config', 
                'view_metrics', 'admin_access'
            ])
        ]
        
        for service_id, permissions in services:
            try:
                self.auth_manager.register_service(service_id, permissions)
            except Exception as e:
                print(f"Warning: Could not register service {service_id}: {e}")
    
    def authenticate_request(self, service_id: str, token: str) -> ServiceContext:
        """Authenticate request and return service context"""
        payload = self.auth_manager.validate_jwt_token(token)
        if not payload:
            raise AuthenticationError("Invalid or expired token")
        
        return ServiceContext(
            service_id=payload['service_id'],
            permissions=payload['permissions']
        )
    
    def create_service_token(self, service_id: str, api_key: str) -> str:
        """Create JWT token for authenticated service"""
        if not self.auth_manager.authenticate_service(service_id, api_key):
            raise AuthenticationError("Invalid service credentials")
        
        return self.auth_manager.generate_jwt_token(service_id)
    
    def encrypt_sensitive_data(self, data: str) -> str:
        """Encrypt sensitive data"""
        return self.encryption.encrypt(data)
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        return self.encryption.decrypt(encrypted_data)
    
    async def secure_http_request(self, method: str, url: str, **kwargs):
        """Make secure HTTP request"""
        return await self.http_client.request(method, url, **kwargs)
    
    def validate_input(self, data: str, input_type: str = 'general') -> bool:
        """Validate input for security"""
        return self.input_validator.validate_input(data, input_type)
    
    def check_resource_limits(self) -> dict:
        """Check current resource usage against limits"""
        return self.resource_manager.check_limits()
    
    def get_security_status(self) -> dict:
        """Get comprehensive security status"""
        return {
            'authentication': {
                'services_registered': len(self.auth_manager.service_registry),
                'active_tokens': len(self.auth_manager.token_cache)
            },
            'resources': self.resource_manager.get_status(),
            'network': {
                'ssl_verification': self.http_client.verify_ssl,
                'allowed_hosts': len(self.http_client.allowed_hosts)
            },
            'encryption': {
                'algorithm': 'fernet',
                'status': 'active'
            }
        }