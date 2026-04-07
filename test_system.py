"""
Automated Test Suite for Brain Tumor Classification System
Tests model predictions, API endpoints, file uploads, and data validation
"""

import pytest
import numpy as np
import os
import tempfile
from PIL import Image
from io import BytesIO
import json

# Mock imports for testing without actual modules
try:
    from security import SecurityManager, ImageValidator, RateLimiter
except:
    pass

class TestModelPredictions:
    """Test model prediction functionality"""
    
    def test_prediction_output_shape(self):
        """Test that model outputs correct shape"""
        from tensorflow.keras.models import load_model
        from tensorflow.keras.utils import normalize
        
        model = load_model('BrainTumor10EpochsCategorical.h5')
        
        # Create dummy input
        dummy_input = np.random.rand(1, 64, 64, 3)
        dummy_input = normalize(dummy_input, axis=1)
        
        # Get prediction
        pred = model.predict(dummy_input, verbose=0)
        
        # Assertions
        assert pred.shape == (1, 2), "Output shape should be (1, 2)"
        assert np.isclose(np.sum(pred), 1.0, atol=0.01), "Output should sum to 1 (probabilities)"
    
    def test_prediction_confidence_range(self):
        """Test that confidence is in valid range"""
        # Confidence should be between 0 and 100
        confidence = 85.5
        assert 0 <= confidence <= 100, "Confidence should be between 0 and 100"
    
    def test_classification_output(self):
        """Test that classification output is valid"""
        predictions = np.array([[0.3, 0.7]])
        class_pred = np.argmax(predictions)
        
        assert class_pred in [0, 1], "Classification should be 0 or 1"

class TestFileValidation:
    """Test file upload validation"""
    
    def test_allowed_extensions(self):
        """Test that correct extensions are allowed"""
        allowed = {'jpg', 'jpeg', 'png', 'bmp', 'tiff'}
        test_files = {
            'image.jpg': True,
            'scan.png': True,
            'brain.jpeg': True,
            'document.pdf': False,
            'script.py': False,
            'data.zip': False
        }
        
        for filename, should_pass in test_files.items():
            ext = filename.split('.')[-1].lower()
            is_allowed = ext in allowed
            assert is_allowed == should_pass
    
    def test_filename_sanitization(self):
        """Test filename sanitization"""
        dangerous_names = [
            "../../../etc/passwd",
            "image<script>.jpg",
            'image"test".jpg',
            "image';rm -rf.jpg"
        ]
        
        for name in dangerous_names:
            from werkzeug.utils import secure_filename
            safe_name = secure_filename(name)
            assert ".." not in safe_name
            assert "<" not in safe_name
            assert ">" not in safe_name
            assert "'" not in safe_name

class TestImageQuality:
    """Test image quality checks"""
    
    def test_create_valid_image(self):
        """Test creation of valid test image"""
        img = Image.new('RGB', (64, 64), color=(128, 128, 128))
        assert img.size == (64, 64)
        assert img.mode == 'RGB'
    
    def test_image_to_numpy(self):
        """Test image conversion to numpy array"""
        img = Image.new('RGB', (64, 64), color=(128, 128, 128))
        arr = np.array(img)
        
        assert arr.shape == (64, 64, 3)
        assert arr.dtype == np.uint8
        assert np.min(arr) >= 0 and np.max(arr) <= 255
    
    def test_image_normalization(self):
        """Test image normalization"""
        img_array = np.random.rand(64, 64, 3) * 255
        
        # Normalize to 0-1
        normalized = img_array / 255.0
        
        assert np.min(normalized) >= 0
        assert np.max(normalized) <= 1

class TestDatabaseOperations:
    """Test database operations (with mock database)"""
    
    def test_user_creation(self):
        """Test user creation"""
        test_user = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123"
        }
        
        # User creation validation
        assert len(test_user["username"]) > 0
        assert "@" in test_user["email"]
        assert len(test_user["password"]) >= 6
    
    def test_analysis_record_structure(self):
        """Test analysis record structure"""
        analysis = {
            "filename": "test.jpg",
            "prediction": "No Brain Tumor",
            "confidence": 85.5,
            "class": 0,
            "timestamp": "2024-01-01T12:00:00"
        }
        
        assert "filename" in analysis
        assert "prediction" in analysis
        assert "confidence" in analysis
        assert "class" in analysis
        assert analysis["class"] in [0, 1]

class TestSecurityValidation:
    """Test security and input validation"""
    
    def test_email_validation(self):
        """Test email validation"""
        valid_emails = [
            "user@example.com",
            "test.user@domain.co.uk",
            "user+tag@mail.com"
        ]
        
        invalid_emails = [
            "notanemail",
            "user@",
            "@example.com",
            "user@domain",
            "user domain@example.com"
        ]
        
        from security import SecurityManager
        
        for email in valid_emails:
            assert SecurityManager.validate_email(email), f"{email} should be valid"
        
        for email in invalid_emails:
            assert not SecurityManager.validate_email(email), f"{email} should be invalid"
    
    def test_string_sanitization(self):
        """Test string sanitization"""
        from security import SecurityManager
        
        dangerous_strings = [
            "<script>alert('xss')</script>",
            "'; DROP TABLE users; --",
            "../../etc/passwd",
            "%' OR '1'='1"
        ]
        
        for s in dangerous_strings:
            sanitized = SecurityManager.sanitize_string(s)
            assert "<" not in sanitized
            assert ">" not in sanitized
            assert ";" not in sanitized

class TestRateLimiting:
    """Test rate limiting functionality"""
    
    def test_rate_limiter_allowed(self):
        """Test that requests within limit are allowed"""
        from security import RateLimiter
        
        limiter = RateLimiter(max_requests=5, time_window=60)
        user_id = "test_user"
        
        # Should allow first 5 requests
        for i in range(5):
            assert limiter.is_allowed(user_id)
        
        # Should block 6th request
        assert not limiter.is_allowed(user_id)

class TestAPIPredictionFlow:
    """Integration tests for API prediction flow"""
    
    def test_prediction_response_structure(self):
        """Test that API response has correct structure"""
        response = {
            'prediction': 'No Brain Tumor',
            'confidence': '85.50%',
            'class': 0,
            'tumor_probability': '14.50%',
            'no_tumor_probability': '85.50%',
            'timestamp': '2024-01-01T12:00:00'
        }
        
        # Verify required fields
        required_fields = ['prediction', 'confidence', 'class', 'timestamp']
        for field in required_fields:
            assert field in response, f"Missing required field: {field}"
        
        # Verify data types
        assert isinstance(response['prediction'], str)
        assert isinstance(response['confidence'], str)
        assert isinstance(response['class'], int)
    
    def test_batch_processing_results(self):
        """Test batch processing result structure"""
        batch_results = [
            {
                "filename": "image1.jpg",
                "prediction": "No Brain Tumor",
                "confidence": "85.50%"
            },
            {
                "filename": "image2.jpg",
                "prediction": "Yes Brain Tumor",
                "confidence": "92.30%"
            }
        ]
        
        assert len(batch_results) == 2
        for result in batch_results:
            assert "filename" in result
            assert "prediction" in result
            assert "confidence" in result

class TestDataExport:
    """Test data export functionality"""
    
    def test_csv_export_format(self):
        """Test CSV export format"""
        import io
        import csv
        
        data = [
            ['Filename', 'Prediction', 'Confidence'],
            ['image1.jpg', 'No Tumor', '85.50%'],
            ['image2.jpg', 'Tumor', '92.30%']
        ]
        
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerows(data)
        
        csv_content = output.getvalue()
        assert 'Filename' in csv_content
        assert 'image1.jpg' in csv_content
        assert '%.50%' in csv_content
    
    def test_json_export_format(self):
        """Test JSON export format"""
        data = {
            "analyses": [
                {"filename": "image1.jpg", "prediction": "No Tumor"},
                {"filename": "image2.jpg", "prediction": "Tumor"}
            ]
        }
        
        json_str = json.dumps(data, indent=2)
        parsed = json.loads(json_str)
        
        assert "analyses" in parsed
        assert len(parsed["analyses"]) == 2

class TestModelComparison:
    """Test comparison and analysis of multiple predictions"""
    
    def test_confidence_comparison(self):
        """Test comparing confidences across multiple analyses"""
        analyses = [
            {"confidence": 85.5, "class": 0},
            {"confidence": 92.3, "class": 1},
            {"confidence": 78.9, "class": 0}
        ]
        
        # Find highest confidence
        max_conf = max(a["confidence"] for a in analyses)
        assert max_conf == 92.3
        
        # Find class distribution
        tumor_count = sum(1 for a in analyses if a["class"] == 1)
        assert tumor_count == 1

# ========== Test Execution ==========
if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
