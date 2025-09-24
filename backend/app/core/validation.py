"""
Input validation utilities and decorators.
"""
import re
import magic
from typing import List, Optional, Set, Dict, Any
from functools import wraps
from pathlib import Path

from ..core.exceptions import ValidationError, FileUploadError


class FileValidator:
    """File upload validation utilities."""
    
    # Allowed MIME types for different file categories
    ALLOWED_VIDEO_TYPES = {
        'video/mp4',
        'video/avi',
        'video/quicktime',
        'video/x-msvideo',
        'video/webm',
        'video/ogg'
    }
    
    ALLOWED_SCRIPT_TYPES = {
        'text/plain',
        'text/rtf',
        'application/pdf',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    }
    
    # File size limits (in bytes)
    MAX_VIDEO_SIZE = 5 * 1024 * 1024 * 1024  # 5GB
    MAX_SCRIPT_SIZE = 50 * 1024 * 1024  # 50MB
    
    @classmethod
    def validate_video_file(cls, file_path: str, file_size: int) -> None:
        """Validate uploaded video file."""
        # Check file size
        if file_size > cls.MAX_VIDEO_SIZE:
            raise FileUploadError(
                f"Video file too large. Maximum size: {cls.MAX_VIDEO_SIZE // (1024*1024*1024)}GB"
            )
        
        # Check MIME type
        mime_type = magic.from_file(file_path, mime=True)
        if mime_type not in cls.ALLOWED_VIDEO_TYPES:
            raise FileUploadError(
                f"Invalid video format. Allowed formats: {', '.join(cls.ALLOWED_VIDEO_TYPES)}"
            )
        
        # Check file extension
        extension = Path(file_path).suffix.lower()
        allowed_extensions = {'.mp4', '.avi', '.mov', '.wmv', '.webm', '.ogv'}
        if extension not in allowed_extensions:
            raise FileUploadError(
                f"Invalid file extension. Allowed extensions: {', '.join(allowed_extensions)}"
            )
    
    @classmethod
    def validate_script_file(cls, file_path: str, file_size: int) -> None:
        """Validate uploaded script file."""
        # Check file size
        if file_size > cls.MAX_SCRIPT_SIZE:
            raise FileUploadError(
                f"Script file too large. Maximum size: {cls.MAX_SCRIPT_SIZE // (1024*1024)}MB"
            )
        
        # Check MIME type
        mime_type = magic.from_file(file_path, mime=True)
        if mime_type not in cls.ALLOWED_SCRIPT_TYPES:
            raise FileUploadError(
                f"Invalid script format. Allowed formats: {', '.join(cls.ALLOWED_SCRIPT_TYPES)}"
            )
        
        # Check file extension
        extension = Path(file_path).suffix.lower()
        allowed_extensions = {'.txt', '.rtf', '.pdf', '.doc', '.docx'}
        if extension not in allowed_extensions:
            raise FileUploadError(
                f"Invalid file extension. Allowed extensions: {', '.join(allowed_extensions)}"
            )


class TextValidator:
    """Text input validation utilities."""
    
    @staticmethod
    def validate_email(email: str) -> None:
        """Validate email format."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            raise ValidationError("Invalid email format", field="email")
    
    @staticmethod
    def validate_password(password: str) -> None:
        """Validate password strength."""
        if len(password) < 8:
            raise ValidationError("Password must be at least 8 characters long", field="password")
        
        if not re.search(r'[A-Z]', password):
            raise ValidationError("Password must contain at least one uppercase letter", field="password")
        
        if not re.search(r'[a-z]', password):
            raise ValidationError("Password must contain at least one lowercase letter", field="password")
        
        if not re.search(r'\d', password):
            raise ValidationError("Password must contain at least one digit", field="password")
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError("Password must contain at least one special character", field="password")
    
    @staticmethod
    def validate_tenant_id(tenant_id: str) -> None:
        """Validate tenant ID format."""
        pattern = r'^[a-zA-Z0-9][a-zA-Z0-9_-]{2,63}$'
        if not re.match(pattern, tenant_id):
            raise ValidationError(
                "Tenant ID must be 3-64 characters, start with alphanumeric, contain only letters, numbers, hyphens, and underscores",
                field="tenant_id"
            )
    
    @staticmethod
    def validate_project_name(name: str) -> None:
        """Validate project name."""
        if not name or len(name.strip()) == 0:
            raise ValidationError("Project name cannot be empty", field="name")
        
        if len(name) > 100:
            raise ValidationError("Project name cannot exceed 100 characters", field="name")
        
        # Check for potentially dangerous characters
        forbidden_chars = ['<', '>', '"', "'", '&', '\n', '\r', '\t']
        if any(char in name for char in forbidden_chars):
            raise ValidationError("Project name contains forbidden characters", field="name")
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename for safe storage."""
        # Remove path separators and dangerous characters
        forbidden_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|', '\0']
        sanitized = filename
        
        for char in forbidden_chars:
            sanitized = sanitized.replace(char, '_')
        
        # Limit length
        if len(sanitized) > 255:
            name, ext = Path(sanitized).stem, Path(sanitized).suffix
            max_name_length = 255 - len(ext)
            sanitized = name[:max_name_length] + ext
        
        return sanitized


class BusinessRuleValidator:
    """Business logic validation utilities."""
    
    @staticmethod
    def validate_processing_options(options: Dict[str, Any]) -> None:
        """Validate video processing options."""
        # Validate resolution
        if 'target_resolution' in options:
            valid_resolutions = ['1080p', '1440p', '4K']
            if options['target_resolution'] not in valid_resolutions:
                raise ValidationError(
                    f"Invalid resolution. Must be one of: {', '.join(valid_resolutions)}",
                    field="target_resolution"
                )
        
        # Validate frame rate
        if 'frame_rate' in options:
            frame_rate = options['frame_rate']
            if not isinstance(frame_rate, (int, float)) or frame_rate <= 0 or frame_rate > 120:
                raise ValidationError(
                    "Frame rate must be a positive number up to 120 fps",
                    field="frame_rate"
                )
        
        # Validate quality settings
        if 'quality' in options:
            valid_qualities = ['low', 'medium', 'high', 'ultra']
            if options['quality'] not in valid_qualities:
                raise ValidationError(
                    f"Invalid quality setting. Must be one of: {', '.join(valid_qualities)}",
                    field="quality"
                )
    
    @staticmethod
    def validate_content_policy(content: str) -> None:
        """Validate content against policy."""
        # Check for obviously problematic content
        forbidden_keywords = [
            'piracy', 'illegal download', 'copyright infringement',
            'stolen content', 'bootleg', 'cam rip'
        ]
        
        content_lower = content.lower()
        for keyword in forbidden_keywords:
            if keyword in content_lower:
                raise ValidationError(
                    f"Content may violate copyright policy: contains '{keyword}'",
                    field="content"
                )
    
    @staticmethod
    def validate_quota_limits(tenant_id: str, resource_type: str, requested_amount: int) -> None:
        """Validate resource usage against quotas."""
        # This would typically check against database quotas
        # For now, implement basic validation
        
        max_limits = {
            'concurrent_jobs': 10,
            'monthly_processing_hours': 100,
            'storage_gb': 1000
        }
        
        if resource_type in max_limits:
            if requested_amount > max_limits[resource_type]:
                raise ValidationError(
                    f"Requested {resource_type} ({requested_amount}) exceeds limit ({max_limits[resource_type]})",
                    field=resource_type
                )


def validate_input(validator_func):
    """Decorator for input validation."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Apply validation
            validator_func(*args, **kwargs)
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def validate_file_upload(file_type: str):
    """Decorator for file upload validation."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract file info from kwargs
            file_path = kwargs.get('file_path')
            file_size = kwargs.get('file_size')
            
            if file_path and file_size:
                if file_type == 'video':
                    FileValidator.validate_video_file(file_path, file_size)
                elif file_type == 'script':
                    FileValidator.validate_script_file(file_path, file_size)
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


class RateLimitValidator:
    """Rate limiting validation utilities."""
    
    @staticmethod
    def validate_rate_limit_config(config: Dict[str, Any]) -> None:
        """Validate rate limit configuration."""
        required_fields = ['requests', 'window', 'burst']
        
        for field in required_fields:
            if field not in config:
                raise ValidationError(f"Missing required field: {field}", field=field)
        
        # Validate numeric values
        if not isinstance(config['requests'], int) or config['requests'] <= 0:
            raise ValidationError("Requests must be a positive integer", field="requests")
        
        if not isinstance(config['window'], int) or config['window'] <= 0:
            raise ValidationError("Window must be a positive integer (seconds)", field="window")
        
        if not isinstance(config['burst'], int) or config['burst'] <= 0:
            raise ValidationError("Burst must be a positive integer", field="burst")
        
        # Logical validation
        if config['burst'] < config['requests']:
            raise ValidationError("Burst limit cannot be less than request limit", field="burst")