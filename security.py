"""
Security and Input Validation Module
Provides security checks, data validation, and input sanitization
"""

import os
import hashlib
import magic
from werkzeug.utils import secure_filename
from PIL import Image
import numpy as np
import re

class SecurityManager:
    """Handle security aspects of the application"""
    
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'bmp', 'tiff'}
    MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB
    ALLOWED_MIME_TYPES = {'image/jpeg', 'image/png', 'image/bmp', 'image/tiff'}
    
    @staticmethod
    def validate_file_upload(file, filename):
        """
        Validate uploaded file
        Args:
            file: File object
            filename: Original filename
        Returns:
            result: Validation result
        """
        # Check filename
        if not filename or filename == '':
            return {"valid": False, "error": "No filename provided"}
        
        # Secure filename
        secure_name = secure_filename(filename)
        if not secure_name:
            return {"valid": False, "error": "Invalid filename"}
        
        # Check extension
        ext = secure_name.split('.')[-1].lower()
        if ext not in SecurityManager.ALLOWED_EXTENSIONS:
            return {"valid": False, "error": f"File type .{ext} not allowed"}
        
        # Check file size
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size == 0:
            return {"valid": False, "error": "File is empty"}
        
        if file_size > SecurityManager.MAX_FILE_SIZE:
            return {"valid": False, "error": "File too large (max 16MB)"}
        
        # Check MIME type using python-magic
        try:
            mime = magic.from_buffer(file.read(1024), mime=True)
            file.seek(0)
            
            if mime not in SecurityManager.ALLOWED_MIME_TYPES:
                return {"valid": False, "error": f"Invalid MIME type: {mime}"}
        except Exception as e:
            print(f"MIME type check warning: {e}")
        
        return {
            "valid": True,
            "filename": secure_name,
            "size": file_size
        }
    
    @staticmethod
    def calculate_file_hash(file_obj):
        """Calculate SHA256 hash of file for integrity checking"""
        sha256_hash = hashlib.sha256()
        file_obj.seek(0)
        
        for byte_block in iter(lambda: file_obj.read(4096), b""):
            sha256_hash.update(byte_block)
        
        file_obj.seek(0)
        return sha256_hash.hexdigest()
    
    @staticmethod
    def sanitize_string(input_str, max_length=255):
        """
        Sanitize user input string
        Args:
            input_str: Input to sanitize
            max_length: Maximum allowed length
        Returns:
            sanitized: Cleaned string
        """
        if not isinstance(input_str, str):
            return ""
        
        # Remove suspicious characters
        sanitized = re.sub(r'[<>\"\'%;)(&+]', '', input_str)
        
        # Remove leading/trailing whitespace
        sanitized = sanitized.strip()
        
        # Limit length
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length]
        
        return sanitized
    
    @staticmethod
    def validate_email(email):
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

class ImageValidator:
    """Validate and preprocess medical images"""
    
    @staticmethod
    def validate_image_content(image_path):
        """
        Validate that file is actually an image
        Args:
            image_path: Path to image file
        Returns:
            result: Validation result
        """
        try:
            img = Image.open(image_path)
            img.verify()
            
            # Reopen after verify (verify closes the file)
            img = Image.open(image_path)
            width, height = img.size
            
            return {
                "valid": True,
                "format": img.format,
                "size": (width, height),
                "mode": img.mode
            }
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    @staticmethod
    def check_image_quality(image_array, min_dimension=32):
        """
        Check if image meets quality requirements
        Args:
            image_array: Numpy image array
            min_dimension: Minimum allowed dimension
        Returns:
            result: Quality assessment
        """
        issues = []
        
        # Check dimensions
        if image_array.shape[0] < min_dimension or image_array.shape[1] < min_dimension:
            issues.append(f"Image too small (min {min_dimension}x{min_dimension})")
        
        # Check if image is mostly blank (low variance)
        if np.var(image_array) < 100:
            issues.append("Image appears to be mostly blank")
        
        # Check histogram
        hist, _ = np.histogram(image_array.flatten(), bins=256, range=(0, 256))
        if np.sum(hist[:10]) > len(image_array.flatten()) * 0.5:
            issues.append("Image appears to be very dark")
        
        if np.sum(hist[-10:]) > len(image_array.flatten()) * 0.5:
            issues.append("Image appears to be very bright")
        
        return {
            "quality_ok": len(issues) == 0,
            "warnings": issues if issues else None,
            "dimensions": image_array.shape,
            "data_type": str(image_array.dtype)
        }
    
    @staticmethod
    def detect_anomalies(image_array):
        """
        Detect anomalies in image that might indicate artifacts
        Args:
            image_array: Image data
        Returns:
            anomalies: List of detected anomalies
        """
        anomalies = []
        
        # Check for extreme values
        if np.any(np.isnan(image_array)):
            anomalies.append("Image contains NaN values")
        
        if np.any(np.isinf(image_array)):
            anomalies.append("Image contains infinite values")
        
        # Check for extreme outliers
        mean = np.mean(image_array)
        std = np.std(image_array)
        outliers = np.sum(np.abs(image_array - mean) > 4 * std)
        
        if outliers > image_array.size * 0.01:  # More than 1% outliers
            anomalies.append("Image contains significant outliers")
        
        return {"has_anomalies": len(anomalies) > 0, "anomalies": anomalies}

class RateLimiter:
    """Simple rate limiting for API endpoints"""
    
    def __init__(self, max_requests=100, time_window=3600):
        """
        Initialize rate limiter
        Args:
            max_requests: Maximum requests allowed
            time_window: Time window in seconds
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = {}
    
    def is_allowed(self, identifier):
        """
        Check if request is allowed
        Args:
            identifier: User/IP identifier
        Returns:
            allowed: Whether request is allowed
        """
        import time
        current_time = time.time()
        
        if identifier not in self.requests:
            self.requests[identifier] = []
        
        # Remove old requests
        self.requests[identifier] = [
            req_time for req_time in self.requests[identifier]
            if current_time - req_time < self.time_window
        ]
        
        # Check if within limit
        if len(self.requests[identifier]) < self.max_requests:
            self.requests[identifier].append(current_time)
            return True
        
        return False
    
    def get_remaining(self, identifier):
        """Get remaining requests for identifier"""
        if identifier not in self.requests:
            return self.max_requests
        
        return max(0, self.max_requests - len(self.requests[identifier]))

print("Security module loaded successfully")
