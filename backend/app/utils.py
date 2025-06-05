# utils.py - Utility Functions and Helpers

import logging
import structlog
import sys
from typing import Any, Dict, List, Optional
import asyncio
import time
import functools
from urllib.parse import urlparse
import re

def setup_logging(level: str = "INFO") -> None:
    """Setup structured logging configuration"""
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, level.upper())
    )
    
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

def validate_url(url: str) -> bool:
    """
    Validate if a URL is properly formatted and accessible
    """
    try:
        # Basic URL validation
        if not url or not isinstance(url, str):
            return False
        
        # Add protocol if missing
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # Parse URL
        parsed = urlparse(url)
        
        # Check if URL has valid scheme and netloc
        if not parsed.scheme or not parsed.netloc:
            return False
        
        # Check for valid domain pattern
        domain_pattern = re.compile(
            r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)*[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?$'
        )
        
        if not domain_pattern.match(parsed.netloc.split(':')[0]):
            return False
        
        return True
        
    except Exception:
        return False

def normalize_url(url: str) -> str:
    """
    Normalize URL by adding protocol if missing and cleaning up
    """
    if not url:
        return url
    
    # Strip whitespace
    url = url.strip()
    
    # Add protocol if missing
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    # Remove trailing slash
    if url.endswith('/'):
        url = url[:-1]
    
    return url

def measure_performance(func):
    """
    Decorator to measure function execution time
    """
    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        start_time = time.time()
        logger = structlog.get_logger()
        
        try:
            result = await func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            logger.info(
                "Function execution completed",
                function=func.__name__,
                execution_time_seconds=round(execution_time, 3),
                status="success"
            )
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            logger.error(
                "Function execution failed",
                function=func.__name__,
                execution_time_seconds=round(execution_time, 3),
                error=str(e),
                status="error"
            )
            
            raise
    
    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs):
        start_time = time.time()
        logger = structlog.get_logger()
        
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            logger.info(
                "Function execution completed",
                function=func.__name__,
                execution_time_seconds=round(execution_time, 3),
                status="success"
            )
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            logger.error(
                "Function execution failed",
                function=func.__name__,
                execution_time_seconds=round(execution_time, 3),
                error=str(e),
                status="error"
            )
            
            raise
    
    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper

def retry_async(max_retries: int = 3, delay: float = 1.0, backoff_factor: float = 2.0):
    """
    Decorator for retrying async functions with exponential backoff
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            logger = structlog.get_logger()
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                    
                except Exception as e:
                    last_exception = e
                    
                    if attempt == max_retries:
                        logger.error(
                            "Function failed after all retries",
                            function=func.__name__,
                            attempt=attempt + 1,
                            max_retries=max_retries,
                            error=str(e)
                        )
                        raise e
                    
                    wait_time = delay * (backoff_factor ** attempt)
                    
                    logger.warning(
                        "Function failed, retrying",
                        function=func.__name__,
                        attempt=attempt + 1,
                        max_retries=max_retries,
                        error=str(e),
                        retry_in_seconds=wait_time
                    )
                    
                    await asyncio.sleep(wait_time)
            
            # This should never be reached, but just in case
            raise last_exception
        
        return wrapper
    return decorator

def retry_sync(max_retries: int = 3, delay: float = 1.0, backoff_factor: float = 2.0):
    """
    Decorator for retrying sync functions with exponential backoff
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger = structlog.get_logger()
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                    
                except Exception as e:
                    last_exception = e
                    
                    if attempt == max_retries:
                        logger.error(
                            "Function failed after all retries",
                            function=func.__name__,
                            attempt=attempt + 1,
                            max_retries=max_retries,
                            error=str(e)
                        )
                        raise e
                    
                    wait_time = delay * (backoff_factor ** attempt)
                    
                    logger.warning(
                        "Function failed, retrying",
                        function=func.__name__,
                        attempt=attempt + 1,
                        max_retries=max_retries,
                        error=str(e),
                        retry_in_seconds=wait_time
                    )
                    
                    time.sleep(wait_time)
            
            # This should never be reached, but just in case
            raise last_exception
        
        return wrapper
    return decorator

def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for safe file system usage
    """
    # Remove or replace invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove leading/trailing spaces and dots
    sanitized = sanitized.strip(' .')
    
    # Limit length
    if len(sanitized) > 200:
        sanitized = sanitized[:200]
    
    # Ensure filename is not empty
    if not sanitized:
        sanitized = "untitled"
    
    return sanitized

def extract_domain(url: str) -> str:
    """
    Extract domain from URL
    """
    try:
        parsed = urlparse(url)
        return parsed.netloc.lower()
    except Exception:
        return ""

def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human readable format
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    import math
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    
    return f"{s} {size_names[i]}"

def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to specified length with suffix
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix

def clean_html_content(html: str) -> str:
    """
    Clean HTML content for processing
    """
    # Remove script and style tags
    html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL | re.IGNORECASE)
    
    # Remove comments
    html = re.sub(r'<!--.*?-->', '', html, flags=re.DOTALL)
    
    # Remove extra whitespace
    html = re.sub(r'\s+', ' ', html)
    
    return html.strip()

def extract_text_from_html(html: str) -> str:
    """
    Extract clean text from HTML content
    """
    from bs4 import BeautifulSoup
    
    try:
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text and clean it
        text = soup.get_text()
        
        # Break into lines and remove leading/trailing space
        lines = (line.strip() for line in text.splitlines())
        
        # Break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        
        # Drop blank lines
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text
        
    except Exception as e:
        logger = structlog.get_logger()
        logger.warning("Failed to extract text from HTML", error=str(e))
        return ""

def create_safe_dict(data: Dict[str, Any], max_depth: int = 10) -> Dict[str, Any]:
    """
    Create a safe dictionary with limited depth to prevent recursion issues
    """
    def _limit_depth(obj, current_depth=0):
        if current_depth >= max_depth:
            return str(obj)
        
        if isinstance(obj, dict):
            return {k: _limit_depth(v, current_depth + 1) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [_limit_depth(item, current_depth + 1) for item in obj[:100]]  # Limit list size
        else:
            return obj
    
    return _limit_depth(data)

def get_file_extension(filename: str) -> str:
    """
    Get file extension from filename
    """
    return filename.split('.')[-1].lower() if '.' in filename else ''

def is_valid_image_url(url: str) -> bool:
    """
    Check if URL appears to be an image
    """
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp'}
    parsed_url = urlparse(url.lower())
    path = parsed_url.path
    
    # Check file extension
    for ext in image_extensions:
        if path.endswith(ext):
            return True
    
    return False

def merge_dicts(*dicts: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge multiple dictionaries, with later dicts taking precedence
    """
    result = {}
    for d in dicts:
        if isinstance(d, dict):
            result.update(d)
    return result

class RateLimiter:
    """
    Simple rate limiter for API calls
    """
    def __init__(self, max_calls: int, time_window: float = 60.0):
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = []
    
    def can_make_call(self) -> bool:
        """Check if a call can be made within rate limits"""
        now = time.time()
        
        # Remove calls outside the time window
        self.calls = [call_time for call_time in self.calls if now - call_time < self.time_window]
        
        return len(self.calls) < self.max_calls
    
    def make_call(self) -> bool:
        """Record a call and return True if within limits"""
        if self.can_make_call():
            self.calls.append(time.time())
            return True
        return False
    
    def time_until_next_call(self) -> float:
        """Get seconds until next call is allowed"""
        if self.can_make_call():
            return 0.0
        
        if not self.calls:
            return 0.0
        
        oldest_call = min(self.calls)
        return self.time_window - (time.time() - oldest_call)

# Initialize logging when module is imported
setup_logging()