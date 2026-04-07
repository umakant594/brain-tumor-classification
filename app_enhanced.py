"""
Enhanced Brain Tumor Classification Flask Application
Includes authentication, database integration, API endpoints, and advanced features
"""

import os
import io
import json
import csv
import tensorflow as tf
import numpy as np
from tensorflow.keras.preprocessing import image
from PIL import Image
import cv2
from tensorflow.keras.models import load_model
from flask import Flask, request, render_template, jsonify, send_file, session
from flask_session import Session
from werkzeug.utils import secure_filename
from tensorflow.keras.utils import normalize
from datetime import datetime, timedelta
import base64

# Import custom modules
try:
    from database import User, Analysis, Patient, Report, demo_db
    from gradcam import generate_heatmap_report
    from security import SecurityManager, ImageValidator, RateLimiter
except ImportError as e:
    print(f"Warning: Could not import custom modules: {e}")

# ========== Flask Setup ==========
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SESSION_TYPE'] = 'filesystem'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
Session(app)

# ========== File Upload Setup ==========
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# ========== Model Loading ==========
model = load_model('BrainTumor10EpochsCategorical.h5')
print('✓ Model loaded. Check http://127.0.0.1:5000/')

# ========== Rate Limiting ==========
api_limiter = RateLimiter(max_requests=100, time_window=3600)

# ========== Helper Functions ==========
def get_className(classNo):
    """Get human-readable class name"""
    if classNo == 0:
        return "No Brain Tumor"
    elif classNo == 1:
        return "Yes Brain Tumor"
    return "Unknown"

def getResult(img_path):
    """
    Get model prediction for image
    Args:
        img_path: Path to image file
    Returns:
        tuple: (class, confidence, prediction)
    """
    try:
        image_data = cv2.imread(img_path)
        image_data = Image.fromarray(image_data, 'RGB')
        image_data = image_data.resize((64, 64))
        image_array = np.array(image_data)
        
        input_img = np.expand_dims(image_array, axis=0)
        input_img = normalize(input_img, axis=1)
        
        prediction = model.predict(input_img, verbose=0)
        confidence = float(np.max(prediction) * 100)
        result_class = int(np.argmax(prediction))
        
        return result_class, confidence, prediction
    except Exception as e:
        print(f"Error in prediction: {e}")
        raise

def process_image_file(file):
    """Process and validate uploaded image file"""
    # Validate file
    validation = SecurityManager.validate_file_upload(file, file.filename)
    if not validation['valid']:
        return {"error": validation['error'], "valid": False}
    
    # Save file
    filename = validation['filename']
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    # Validate image content
    img_validation = ImageValidator.validate_image_content(filepath)
    if not img_validation['valid']:
        os.remove(filepath)
        return {"error": "Invalid image file", "valid": False}
    
    return {
        "valid": True,
        "filepath": filepath,
        "filename": filename,
        "size": img_validation['size']
    }

# ========== Core Routes ==========
@app.route('/', methods=['GET'])
def index():
    """Serve main application interface"""
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    """
    Main prediction endpoint
    Returns JSON with prediction results
    """
    try:
        # Rate limiting
        user_ip = request.remote_addr
        if not api_limiter.is_allowed(user_ip):
            return jsonify({"error": "Rate limit exceeded"}), 429
        
        # Check file
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400
        
        # Process file
        result = process_image_file(file)
        if not result['valid']:
            return jsonify({"error": result['error']}), 400
        
        filepath = result['filepath']
        
        # Get prediction
        result_class, confidence, prediction = getResult(filepath)
        result_text = get_className(result_class)
        
        # Prepare response
        response_data = {
            'prediction': result_text,
            'confidence': f'{confidence:.2f}%',
            'class': result_class,
            'tumor_probability': f'{float(prediction[0][1])*100:.2f}%',
            'no_tumor_probability': f'{float(prediction[0][0])*100:.2f}%',
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Save to database if user is logged in
        if 'user_id' in session:
            Analysis.save(session['user_id'], result['filename'], response_data)
        
        # Cleanup
        try:
            os.remove(filepath)
        except:
            pass
        
        return jsonify(response_data)
    
    except Exception as e:
        return jsonify({"error": f"Prediction error: {str(e)}"}), 500

@app.route('/predict/heatmap', methods=['POST'])
def predict_with_heatmap():
    """
    Prediction with Grad-CAM heatmap visualization
    """
    try:
        # Check file
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        
        # Process file
        result = process_image_file(file)
        if not result['valid']:
            return jsonify({"error": result['error']}), 400
        
        filepath = result['filepath']
        
        # Get prediction
        result_class, confidence, prediction = getResult(filepath)
        
        # Prepare image for heatmap
        image_data = cv2.imread(filepath)
        image_data = cv2.cvtColor(image_data, cv2.COLOR_BGR2RGB)
        image_data = cv2.resize(image_data, (64, 64))
        image_array = np.array(image_data)
        input_img = np.expand_dims(image_array, axis=0)
        input_img = normalize(input_img, axis=1)
        
        # Generate heatmap
        heatmap_result = generate_heatmap_report(model, input_img, layer_name="conv2d")
        
        # Prepare response
        response_data = {
            'prediction': get_className(result_class),
            'confidence': f'{confidence:.2f}%',
            'class': result_class,
            'tumor_probability': f'{float(prediction[0][1])*100:.2f}%',
            'no_tumor_probability': f'{float(prediction[0][0])*100:.2f}%',
            'heatmap': heatmap_result['heatmap_image'] if heatmap_result['success'] else None,
            'heatmap_explanation': heatmap_result.get('explanation', 'Heatmap generation failed'),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Cleanup
        try:
            os.remove(filepath)
        except:
            pass
        
        return jsonify(response_data)
    
    except Exception as e:
        return jsonify({"error": f"Heatmap error: {str(e)}"}), 500

@app.route('/api/export/<format_type>', methods=['GET'])
def export_analysis(format_type):
    """
    Export analysis history in various formats
    Formats: json, csv, pdf
    """
    if 'user_id' not in session:
        return jsonify({"error": "Not authenticated"}), 401
    
    try:
        analyses = Analysis.get_user_history(session['user_id'])
        
        if format_type == 'json':
            # Convert ObjectId to string for JSON serialization
            analyses_json = json.dumps([{
                'filename': a['filename'],
                'prediction': a['prediction'],
                'confidence': a['confidence'],
                'timestamp': a['timestamp'].isoformat()
            } for a in analyses], indent=2)
            
            return send_file(
                io.BytesIO(analyses_json.encode()),
                mimetype='application/json',
                as_attachment=True,
                download_name=f"analyses_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
        
        elif format_type == 'csv':
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(['Filename', 'Prediction', 'Confidence', 'Timestamp'])
            
            for a in analyses:
                writer.writerow([
                    a['filename'],
                    a['prediction'],
                    a['confidence'],
                    a['timestamp']
                ])
            
            return send_file(
                io.BytesIO(output.getvalue().encode()),
                mimetype='text/csv',
                as_attachment=True,
                download_name=f"analyses_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            )
        
        else:
            return jsonify({"error": "Unsupported format"}), 400
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/history', methods=['GET'])
def get_history():
    """Get analysis history for current user"""
    if 'user_id' not in session:
        return jsonify([])
    
    try:
        analyses = Analysis.get_user_history(session['user_id'], limit=20)
        history = [{
            'filename': a['filename'],
            'prediction': a['prediction'],
            'confidence': a['confidence'],
            'timestamp': a['timestamp'].isoformat()
        } for a in analyses]
        
        return jsonify(history)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get overall application statistics"""
    try:
        stats = Analysis.get_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ========== Authentication Routes ==========
@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register new user"""
    try:
        data = request.json
        username = SecurityManager.sanitize_string(data.get('username', ''))
        email = data.get('email', '')
        password = data.get('password', '')
        
        # Validate inputs
        if not username or not email or not password:
            return jsonify({"error": "Missing required fields"}), 400
        
        if not SecurityManager.validate_email(email):
            return jsonify({"error": "Invalid email format"}), 400
        
        if len(password) < 6:
            return jsonify({"error": "Password must be at least 6 characters"}), 400
        
        # Create user
        result = User.create(username, email, password)
        return jsonify(result), 201 if result['success'] else 400
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login user"""
    try:
        data = request.json
        username = data.get('username', '')
        password = data.get('password', '')
        
        if not username or not password:
            return jsonify({"error": "Missing credentials"}), 400
        
        user = User.verify(username, password)
        if not user:
            return jsonify({"error": "Invalid credentials"}), 401
        
        session['user_id'] = str(user.get('_id', username))
        session['username'] = username
        
        return jsonify({"success": True, "message": "Logged in successfully"})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    """Logout user"""
    session.clear()
    return jsonify({"success": True, "message": "Logged out successfully"})

# ========== Error Handlers ==========
@app.errorhandler(413)
def too_large(e):
    """Handle file too large error"""
    return jsonify({"error": "File too large. Maximum size is 16MB"}), 413

@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    if request.path.startswith('/api/'):
        return jsonify({"error": "Endpoint not found"}), 404
    return render_template('index.html')

# ========== Main ==========
if __name__ == '__main__':
    print("\n" + "="*50)
    print("🧠 Brain Tumor Classification System")
    print("="*50)
    print("✓ Model loaded successfully")
    print("✓ Database module ready")
    print("✓ Security checks enabled")
    print("\n🌐 Starting server at http://127.0.0.1:5000/")
    print("="*50 + "\n")
    
    app.run(debug=True, host='127.0.0.1', port=5000)
