# 🔌 API Documentation

Complete REST API reference for the Brain Tumor Classification System.

---

## Base URL
```
http://localhost:5000
```

---

## Authentication Endpoints

### Register User
```
POST /api/auth/register
```

**Request:**
```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "securepassword123"
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "user_id": "507f1f77bcf86cd799439011"
}
```

**Errors:**
- 400: Missing required fields, invalid email, or weak password
- 409: User already exists

---

### Login
```
POST /api/auth/login
```

**Request:**
```json
{
  "username": "john_doe",
  "password": "securepassword123"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Logged in successfully"
}
```

**Errors:**
- 400: Missing credentials
- 401: Invalid credentials

---

### Logout
```
POST /api/auth/logout
```

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Logged out successfully"
}
```

---

## Prediction Endpoints

### Basic Prediction
```
POST /predict
Content-Type: multipart/form-data
```

**Request:**
```
file: <image file>
```

**Response (200 OK):**
```json
{
  "prediction": "No Brain Tumor",
  "confidence": "85.50%",
  "class": 0,
  "tumor_probability": "14.50%",
  "no_tumor_probability": "85.50%",
  "timestamp": "2024-01-01T12:00:00.000000"
}
```

**Response Classes:**
- `0`: No Brain Tumor
- `1`: Yes Brain Tumor

**Errors:**
- 400: No file provided, invalid file format
- 413: File too large (> 16MB)
- 429: Rate limit exceeded
- 500: Prediction error

---

### Prediction with Heatmap
```
POST /predict/heatmap
Content-Type: multipart/form-data
```

**Request:**
```
file: <image file>
```

**Response (200 OK):**
```json
{
  "prediction": "Yes Brain Tumor",
  "confidence": "92.30%",
  "class": 1,
  "tumor_probability": "92.30%",
  "no_tumor_probability": "7.70%",
  "heatmap": "data:image/png;base64,iVBORw0KGgoAAAANS...",
  "heatmap_explanation": "Red regions indicate areas the model considers as having tumor characteristics...",
  "timestamp": "2024-01-01T12:00:00.000000"
}
```

**Heatmap Format:**
- Base64-encoded PNG image
- Red: High tumor probability
- Blue: Low tumor probability
- Grayscale: Neutral regions

---

## Analysis History Endpoints

### Get Analysis History
```
GET /api/history
```

**Authorization:** Requires active session (login required)

**Response (200 OK):**
```json
[
  {
    "filename": "brain_scan_001.jpg",
    "prediction": "No Brain Tumor",
    "confidence": "85.50%",
    "timestamp": "2024-01-01T12:00:00.000000"
  },
  {
    "filename": "brain_scan_002.jpg",
    "prediction": "Yes Brain Tumor",
    "confidence": "92.30%",
    "timestamp": "2024-01-01T13:15:00.000000"
  }
]
```

**Errors:**
- 401: Not authenticated

---

## Data Export Endpoints

### Export as CSV
```
GET /api/export/csv
```

**Authorization:** Requires active session (login required)

**Response (200 OK):**
```
Content-Type: text/csv
Content-Disposition: attachment; filename="analyses_20240101_120000.csv"

Filename,Prediction,Confidence,Timestamp
brain_scan_001.jpg,No Brain Tumor,85.50%,2024-01-01T12:00:00
brain_scan_002.jpg,Yes Brain Tumor,92.30%,2024-01-01T13:15:00
```

---

### Export as JSON
```
GET /api/export/json
```

**Authorization:** Requires active session (login required)

**Response (200 OK):**
```json
[
  {
    "filename": "brain_scan_001.jpg",
    "prediction": "No Brain Tumor",
    "confidence": "85.50%",
    "timestamp": "2024-01-01T12:00:00.000000"
  },
  {
    "filename": "brain_scan_002.jpg",
    "prediction": "Yes Brain Tumor",
    "confidence": "92.30%",
    "timestamp": "2024-01-01T13:15:00.000000"
  }
]
```

---

## Statistics Endpoints

### Get Overall Statistics
```
GET /api/stats
```

**Response (200 OK):**
```json
{
  "total_analyses": 152,
  "tumor_detected": 38,
  "normal": 114,
  "tumor_percentage": 25.0
}
```

---

## Error Responses

### Standard Error Format
```json
{
  "error": "Error message describing what went wrong"
}
```

### Common HTTP Status Codes
| Code | Meaning | Reason |
|------|---------|--------|
| 200 | OK | Successful request |
| 201 | Created | Resource created successfully |
| 400 | Bad Request | Invalid input or missing fields |
| 401 | Unauthorized | Authentication required or failed |
| 404 | Not Found | Endpoint or resource not found |
| 413 | Payload Too Large | File exceeds size limit |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Server Error | Internal server error |

---

## Rate Limiting

**Limit:** 100 requests per hour per IP address

**Headers:**
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 75
X-RateLimit-Reset: 1609502400
```

**When Exceeded:**
```json
{
  "error": "Rate limit exceeded"
}
```
Status: `429 Too Many Requests`

---

## File Upload Specifications

### Supported Formats
- JPEG (.jpg, .jpeg)
- PNG (.png)
- BMP (.bmp)
- TIFF (.tiff)

### Size Limits
- **Maximum**: 16 MB
- **Minimum**: 1 byte (validated for image content)

### Recommended Image Specifications
- **Dimensions**: 64×64 pixels (will be resized)
- **Format**: MRI or CT scan cross-sections
- **Quality**: High contrast for better accuracy

---

## Request Examples

### Using cURL
```bash
# Basic prediction
curl -X POST http://localhost:5000/predict \
  -F "file=@brain_scan.jpg"

# Prediction with heatmap
curl -X POST http://localhost:5000/predict/heatmap \
  -F "file=@brain_scan.jpg"

# Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"john_doe","password":"pass123"}'

# Get history
curl -X GET http://localhost:5000/api/history \
  -b "session_cookie"

# Export as CSV
curl -X GET http://localhost:5000/api/export/csv \
  -b "session_cookie" \
  -o analyses.csv
```

### Using Python (Requests)
```python
import requests

# Basic prediction
files = {'file': open('brain_scan.jpg', 'rb')}
response = requests.post('http://localhost:5000/predict', files=files)
print(response.json())

# Login
data = {
    'username': 'john_doe',
    'password': 'securepassword123'
}
response = requests.post('http://localhost:5000/api/auth/login', json=data)
print(response.json())

# Get history (with session)
session = requests.Session()
session.post('http://localhost:5000/api/auth/login', json=data)
response = session.get('http://localhost:5000/api/history')
print(response.json())
```

### Using JavaScript (Fetch)
```javascript
// Basic prediction
async function predict(file) {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetch('http://localhost:5000/predict', {
    method: 'POST',
    body: formData
  });
  
  return await response.json();
}

// Login
async function login(username, password) {
  const response = await fetch('http://localhost:5000/api/auth/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({username, password})
  });
  
  return await response.json();
}

// Get history
async function getHistory() {
  const response = await fetch('http://localhost:5000/api/history');
  return await response.json();
}
```

---

## Response Headers

### Standard Headers
```
Content-Type: application/json
X-Content-Type-Options: nosniff
X-Frame-Options: SAMEORIGIN
X-XSS-Protection: 1; mode=block
```

---

## Versioning

**Current API Version:** 1.0

To access a specific version, use:
```
/api/v1/predict
```

---

## Webhooks (Future)

Planned webhook support for real-time notifications:
```
POST /api/webhooks/register
{
  "url": "https://yourserver.com/webhook",
  "events": ["prediction.complete", "analysis.stored"]
}
```

---

## Rate Limiting Details

### Per-IP Rate Limiting
- Window: 1 hour (3600 seconds)
- Limit: 100 requests
- Strategy: Sliding window

### Per-User Rate Limiting (Authenticated)
- Window: 1 hour
- Limit: 500 requests
- Allows higher limits for registered users

---

## API Health Check

### Get Server Status
```
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "model": "loaded",
  "database": "connected",
  "uptime": "2 hours 30 minutes"
}
```

---

## Batch Processing

### Submit Batch Job
```
POST /api/batch
Content-Type: application/json
```

**Request:**
```json
{
  "files": ["scan1.jpg", "scan2.jpg", "scan3.jpg"],
  "callback_url": "https://yourserver.com/callback"
}
```

**Response:**
```json
{
  "batch_id": "batch_507f1f77bcf86cd799439011",
  "status": "processing",
  "total_files": 3,
  "progress": 0
}
```

### Get Batch Status
```
GET /api/batch/{batch_id}
```

---

## Changelog

### Version 1.0 (Current)
- Basic prediction endpoint
- Heatmap visualization
- User authentication
- History tracking
- CSV/JSON export
- Rate limiting
- File validation

### Version 0.9
- Basic prediction functionality
- Single image uploads

---

## Support

For API issues:
1. Check error response for details
2. Verify input format and size limits
3. Check server logs at `logs/app.log`
4. Contact: support@braintumor.ai

---

**Last Updated**: April 2026
**Maintained By**: Development Team
