"""
Database and User Management Module
Integrates MongoDB for patient records, analysis history, and user authentication
"""

from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# MongoDB Connection
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
DB_NAME = os.getenv('DB_NAME', 'brain_tumor_db')

try:
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    print("✓ MongoDB connected successfully")
except Exception as e:
    print(f"⚠ MongoDB connection failed: {e}")
    print("Running in demo mode without database persistence")
    db = None

class User:
    """User model for authentication"""
    
    @staticmethod
    def create(username, email, password):
        """Create new user"""
        if db is None:
            return {"success": False, "error": "Database not available"}
        
        if db.users.find_one({"$or": [{"username": username}, {"email": email}]}):
            return {"success": False, "error": "User already exists"}
        
        user = {
            "username": username,
            "email": email,
            "password_hash": generate_password_hash(password),
            "created_at": datetime.utcnow(),
            "is_doctor": False,
            "profile": {}
        }
        result = db.users.insert_one(user)
        return {"success": True, "user_id": str(result.inserted_id)}
    
    @staticmethod
    def verify(username, password):
        """Verify user credentials"""
        if db is None:
            return None
        
        user = db.users.find_one({"username": username})
        if user and check_password_hash(user["password_hash"], password):
            return user
        return None
    
    @staticmethod
    def get(username):
        """Get user by username"""
        if db is None:
            return None
        return db.users.find_one({"username": username})

class Analysis:
    """Analysis record model"""
    
    @staticmethod
    def save(user_id, filename, result, image_base64=None):
        """Save analysis result"""
        if db is None:
            return {"success": False, "error": "Database not available"}
        
        analysis = {
            "user_id": user_id,
            "filename": filename,
            "prediction": result.get("prediction"),
            "confidence": result.get("confidence"),
            "class": result.get("class"),
            "tumor_probability": result.get("tumor_probability"),
            "no_tumor_probability": result.get("no_tumor_probability"),
            "timestamp": datetime.utcnow(),
            "image_base64": image_base64 if image_base64 else None,
            "tags": []
        }
        result = db.analyses.insert_one(analysis)
        return {"success": True, "analysis_id": str(result.inserted_id)}
    
    @staticmethod
    def get_user_history(user_id, limit=20):
        """Get user's analysis history"""
        if db is None:
            return []
        
        return list(db.analyses.find(
            {"user_id": user_id}
        ).sort("timestamp", -1).limit(limit))
    
    @staticmethod
    def get_stats():
        """Get overall statistics"""
        if db is None:
            return {}
        
        total = db.analyses.count_documents({})
        tumors = db.analyses.count_documents({"class": 1})
        normal = db.analyses.count_documents({"class": 0})
        
        return {
            "total_analyses": total,
            "tumor_detected": tumors,
            "normal": normal,
            "tumor_percentage": (tumors / total * 100) if total > 0 else 0
        }

class Patient:
    """Patient record model"""
    
    @staticmethod
    def create(user_id, patient_data):
        """Create patient profile"""
        if db is None:
            return {"success": False, "error": "Database not available"}
        
        patient = {
            "user_id": user_id,
            "name": patient_data.get("name"),
            "age": patient_data.get("age"),
            "gender": patient_data.get("gender"),
            "medical_history": patient_data.get("medical_history", []),
            "created_at": datetime.utcnow(),
            "last_updated": datetime.utcnow()
        }
        result = db.patients.insert_one(patient)
        return {"success": True, "patient_id": str(result.inserted_id)}
    
    @staticmethod
    def get(user_id):
        """Get patient record"""
        if db is None:
            return None
        return db.patients.find_one({"user_id": user_id})

class Report:
    """Analysis report model"""
    
    @staticmethod
    def generate_pdf_data(analysis_id):
        """Generate PDF report data"""
        if db is None:
            return None
        
        from bson.objectid import ObjectId
        analysis = db.analyses.find_one({"_id": ObjectId(analysis_id)})
        if not analysis:
            return None
        
        return {
            "title": "Brain Tumor Detection Analysis Report",
            "analysis_id": str(analysis["_id"]),
            "date": analysis["timestamp"].strftime("%Y-%m-%d %H:%M:%S"),
            "filename": analysis["filename"],
            "prediction": analysis["prediction"],
            "confidence": analysis["confidence"],
            "tumor_prob": analysis["tumor_probability"],
            "normal_prob": analysis["no_tumor_probability"],
            "disclaimer": "This is an AI-generated report for educational purposes. Always consult medical professionals."
        }

# Demo/Mock Database for testing without MongoDB
class DemoDatabase:
    """In-memory demo database for testing"""
    
    def __init__(self):
        self.users = {}
        self.analyses = []
        self.patients = {}
        self.user_counter = 0
        self.analysis_counter = 0
    
    def add_user(self, username, email, password):
        self.user_counter += 1
        self.users[self.user_counter] = {
            "id": self.user_counter,
            "username": username,
            "email": email,
            "password_hash": generate_password_hash(password),
            "created_at": datetime.utcnow()
        }
        return self.user_counter
    
    def get_user(self, username):
        for user in self.users.values():
            if user["username"] == username:
                return user
        return None
    
    def add_analysis(self, user_id, analysis_data):
        self.analysis_counter += 1
        analysis_data["id"] = self.analysis_counter
        analysis_data["user_id"] = user_id
        analysis_data["timestamp"] = datetime.utcnow()
        self.analyses.append(analysis_data)
        return self.analysis_counter
    
    def get_user_analyses(self, user_id, limit=20):
        return [a for a in self.analyses if a["user_id"] == user_id][:limit]

# Use demo database if MongoDB is not available
if db is None:
    demo_db = DemoDatabase()
else:
    demo_db = None

print("Database module loaded successfully")
