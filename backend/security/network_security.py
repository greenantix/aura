import ssl
import certifi
import httpx
from typing import Dict, Any
from urllib.parse import urlparse

class SecurityError(Exception):
    """Security-related error"""
    pass

class SecureHTTPClient:
    """Secure HTTP client with proper TLS validation"""

    def __init__(self, config: Dict[str, Any]):
        self.timeout = config.get('timeout', 30)
        self.verify_ssl = config.get('verify_ssl', True)
        self.allowed_hosts = config.get('allowed_hosts', [])

        # Create SSL context with strong security
        self.ssl_context = ssl.create_default_context(cafile=certifi.where())
        self.ssl_context.check_hostname = True
        self.ssl_context.verify_mode = ssl.CERT_REQUIRED
        self.ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2

    async def request(self, method: str, url: str, **kwargs) -> httpx.Response:
        """Make secure HTTP request with validation"""
        if not self._is_url_allowed(url):
            raise SecurityError(f"Access to URL not permitted: {url}")

        # Set security headers
        headers = kwargs.get('headers', {})
        headers.update({
            'User-Agent': 'Aura/2.0 Security-Enhanced',
            'Accept': 'application/json',
            'Connection': 'close'
        })
        kwargs['headers'] = headers

        # Configure SSL verification
        if self.verify_ssl:
            kwargs['verify'] = self.ssl_context

        # Set timeout
        kwargs['timeout'] = self.timeout

        async with httpx.AsyncClient() as client:
            response = await client.request(method, url, **kwargs)
            self._validate_response(response)
            return response

    def _is_url_allowed(self, url: str) -> bool:
        """Check if URL is in allowed hosts list"""
        if not self.allowed_hosts:
            return True  # No restrictions if list is empty
        parsed = urlparse(url)
        return parsed.hostname in self.allowed_hosts

    def _validate_response(self, response: httpx.Response):
        """Validate HTTP response for security"""
        content_length = response.headers.get('content-length')
        if content_length and int(content_length) > 10 * 1024 * 1024:  # 10MB limit
            raise SecurityError("Response size exceeds limit")

        content_type = response.headers.get('content-type', '')
        allowed_types = ['application/json', 'text/plain', 'application/xml']
        if not any(allowed in content_type for allowed in allowed_types):
            raise SecurityError(f"Disallowed content type: {content_type}")