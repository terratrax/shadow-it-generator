"""HTTP response generation.

This module handles generation of realistic HTTP responses including
status codes, response sizes, and file types.
"""

import random
from typing import Dict, Tuple, Optional
from enum import Enum


class FileType(Enum):
    """Common file types for web requests."""
    HTML = "text/html"
    JSON = "application/json"
    XML = "application/xml"
    JS = "application/javascript"
    CSS = "text/css"
    IMAGE_JPEG = "image/jpeg"
    IMAGE_PNG = "image/png"
    IMAGE_GIF = "image/gif"
    PDF = "application/pdf"
    DOCX = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    ZIP = "application/zip"
    BINARY = "application/octet-stream"
    NONE = ""


class ResponseGenerator:
    """Generates realistic HTTP responses.
    
    This class creates appropriate response codes, sizes, and metadata
    based on the request context and service configuration.
    """
    
    def __init__(self):
        """Initialize the response generator."""
        # Status code probabilities for allowed requests
        self.allowed_status_weights = {
            200: 0.92,  # OK
            201: 0.02,  # Created (for POST)
            204: 0.01,  # No Content
            301: 0.01,  # Moved Permanently
            302: 0.01,  # Found (redirect)
            304: 0.02,  # Not Modified
            404: 0.01,  # Not Found
        }
        
        # File type detection patterns
        self.file_extensions = {
            '.html': FileType.HTML,
            '.htm': FileType.HTML,
            '.json': FileType.JSON,
            '.xml': FileType.XML,
            '.js': FileType.JS,
            '.css': FileType.CSS,
            '.jpg': FileType.IMAGE_JPEG,
            '.jpeg': FileType.IMAGE_JPEG,
            '.png': FileType.IMAGE_PNG,
            '.gif': FileType.IMAGE_GIF,
            '.pdf': FileType.PDF,
            '.docx': FileType.DOCX,
            '.xlsx': FileType.XLSX,
            '.zip': FileType.ZIP,
        }
    
    def generate_response(self,
                         method: str,
                         url: str,
                         is_allowed: bool,
                         is_api: bool = False) -> Dict[str, any]:
        """Generate HTTP response details.
        
        Args:
            method: HTTP method
            url: Request URL
            is_allowed: Whether request is allowed
            is_api: Whether this is an API endpoint
            
        Returns:
            Dictionary with response details
        """
        if not is_allowed:
            # Blocked request
            return {
                'status_code': 403,
                'file_type': FileType.HTML.value,
                'response_size': random.randint(1000, 5000),
                'response_time': random.randint(10, 50)
            }
        
        # Generate status code
        status_code = self._generate_status_code(method)
        
        # Determine file type
        file_type = self._detect_file_type(url, is_api)
        
        # Generate response size
        response_size = self._generate_response_size(
            method, status_code, file_type, is_api
        )
        
        # Generate response time
        response_time = self._generate_response_time(response_size)
        
        return {
            'status_code': status_code,
            'file_type': file_type.value if file_type != FileType.NONE else '',
            'response_size': response_size,
            'response_time': response_time
        }
    
    def _generate_status_code(self, method: str) -> int:
        """Generate appropriate status code.
        
        Args:
            method: HTTP method
            
        Returns:
            HTTP status code
        """
        # Adjust weights based on method
        weights = self.allowed_status_weights.copy()
        
        if method == 'POST':
            weights[201] = 0.10  # More likely to return Created
            weights[200] = 0.85
        elif method == 'DELETE':
            weights[204] = 0.20  # More likely to return No Content
            weights[200] = 0.75
        elif method == 'HEAD':
            weights[200] = 0.95
            weights[404] = 0.05
        
        # Select status code
        codes = list(weights.keys())
        probabilities = list(weights.values())
        
        # Normalize probabilities
        total = sum(probabilities)
        probabilities = [p/total for p in probabilities]
        
        return random.choices(codes, weights=probabilities)[0]
    
    def _detect_file_type(self, url: str, is_api: bool) -> FileType:
        """Detect file type from URL.
        
        Args:
            url: Request URL
            is_api: Whether this is an API endpoint
            
        Returns:
            FileType enum value
        """
        # API endpoints typically return JSON
        if is_api:
            return FileType.JSON
        
        # Check URL path for file extension
        path = url.split('?')[0].lower()
        
        for ext, file_type in self.file_extensions.items():
            if path.endswith(ext):
                return file_type
        
        # Default based on path patterns
        if '/api/' in path or '/v1/' in path or '/v2/' in path:
            return FileType.JSON
        elif path.endswith('/') or not '.' in path.split('/')[-1]:
            return FileType.HTML
        else:
            return FileType.BINARY
    
    def _generate_response_size(self,
                               method: str,
                               status_code: int,
                               file_type: FileType,
                               is_api: bool) -> int:
        """Generate realistic response size.
        
        Args:
            method: HTTP method
            status_code: HTTP status code
            file_type: Type of content
            is_api: Whether this is an API call
            
        Returns:
            Response size in bytes
        """
        # Special cases
        if method == 'HEAD' or status_code == 204:
            return 0
        
        if status_code >= 400:
            # Error responses are typically small
            return random.randint(200, 2000)
        
        # Size ranges by file type
        size_ranges = {
            FileType.HTML: (5_000, 150_000),
            FileType.JSON: (100, 50_000) if is_api else (1_000, 500_000),
            FileType.XML: (1_000, 100_000),
            FileType.JS: (1_000, 500_000),
            FileType.CSS: (1_000, 100_000),
            FileType.IMAGE_JPEG: (20_000, 2_000_000),
            FileType.IMAGE_PNG: (10_000, 1_000_000),
            FileType.IMAGE_GIF: (5_000, 500_000),
            FileType.PDF: (50_000, 10_000_000),
            FileType.DOCX: (20_000, 5_000_000),
            FileType.XLSX: (10_000, 5_000_000),
            FileType.ZIP: (1_000, 50_000_000),
            FileType.BINARY: (1_000, 10_000_000),
        }
        
        min_size, max_size = size_ranges.get(file_type, (1_000, 100_000))
        
        # Use log-normal distribution for more realistic sizes
        import math
        mean = math.log((min_size + max_size) / 2)
        sigma = 0.5
        size = int(random.lognormvariate(mean, sigma))
        
        # Clamp to range
        return max(min_size, min(size, max_size))
    
    def _generate_response_time(self, response_size: int) -> int:
        """Generate response time based on size and other factors.
        
        Args:
            response_size: Size of response in bytes
            
        Returns:
            Response time in milliseconds
        """
        # Base latency
        base_latency = random.randint(20, 100)
        
        # Size-based component (assume 10 Mbps connection)
        size_ms = (response_size * 8) / (10 * 1000)  # Convert to milliseconds
        
        # Processing time (varies by size)
        if response_size < 10_000:
            processing = random.randint(5, 20)
        elif response_size < 100_000:
            processing = random.randint(20, 50)
        else:
            processing = random.randint(50, 200)
        
        # Total time with some randomness
        total = base_latency + size_ms + processing
        
        # Add random variance
        variance = random.uniform(0.8, 1.2)
        
        return max(1, int(total * variance))
    
    def generate_block_reason(self, category: str) -> Tuple[str, int]:
        """Generate block reason and code.
        
        Args:
            category: Service category
            
        Returns:
            Tuple of (reason_text, reason_code)
        """
        block_reasons = {
            'File Sharing': ("Unsanctioned File Sharing", 1001),
            'Personal Storage': ("Personal Cloud Storage Blocked", 1002),
            'Social Media': ("Social Media Access Denied", 1003),
            'Personal Email': ("Personal Email Blocked", 1004),
            'VPN': ("VPN Service Blocked", 1005),
            'Proxy': ("Anonymous Proxy Blocked", 1006),
            'Torrent': ("P2P/Torrent Site Blocked", 1007),
            'Cryptocurrency': ("Cryptocurrency Site Blocked", 1008),
            'Gambling': ("Gambling Site Blocked", 1009),
            'Adult Content': ("Adult Content Blocked", 1010),
            'Unknown': ("Uncategorized Site Blocked", 1099),
        }
        
        return block_reasons.get(category, ("Policy Violation", 1000))