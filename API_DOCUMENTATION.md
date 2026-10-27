# API Documentation - AI Smart Safety Monitoring System

## Base URL
```
http://localhost:5000
```

## Authentication
Currently no authentication required. Implement JWT tokens for production.

---

## Monitoring Control Endpoints

### Start Monitoring
```
POST /api/start_monitoring
Content-Type: application/json

Response: 200 OK
{
  "status": "success",
  "message": "Monitoring started"
}
```

### Stop Monitoring
```
POST /api/stop_monitoring
Content-Type: application/json

Response: 200 OK
{
  "status": "success",
  "message": "Monitoring stopped"
}
```

### Video Feed
```
GET /video_feed

Response: 200 OK
Content-Type: multipart/x-mixed-replace; boundary=frame
(Binary video stream in MJPEG format)
```

---

## Data Retrieval Endpoints

### Get Incidents
```
GET /api/incidents?limit=50

Query Parameters:
  limit (int, optional): Maximum number of incidents to return (default: 50)

Response: 200 OK
{
  "incidents": [
    {
      "id": 1,
      "type": "MISSING_HELMET",
      "severity": "HIGH",
      "timestamp": "2024-03-17T12:30:45.123456",
      "details": {
        "workers_detected": 5,
        "helmets_detected": 4,
        "violations": ["MISSING_HELMET"],
        "confidence": 0.8,
        "frame_shape": [480, 640, 3]
      }
    }
  ]
}
```

### Get Active Alerts
```
GET /api/alerts

Response: 200 OK
{
  "alerts": [
    {
      "id": 1,
      "type": "MISSING_HELMET",
      "message": "Safety violation detected: MISSING_HELMET",
      "timestamp": "2024-03-17T12:30:45.123456",
      "is_active": true
    }
  ]
}
```

### Get Statistics
```
GET /api/statistics

Response: 200 OK
{
  "total_incidents": 125,
  "today_incidents": 8,
  "high_severity": 15,
  "safety_score": 87,
  "monitoring_status": "Active"
}
```

---

## Configuration Endpoints

### Get Alert Configuration
```
GET /api/alert_config

Response: 200 OK
{
  "threshold": 5,
  "sound_alerts": true,
  "email_alerts": true
}
```

### Update Alert Configuration
```
POST /api/alert_config
Content-Type: application/json

Request Body:
{
  "threshold": 5,
  "sound_alerts": true,
  "email_alerts": true
}

Response: 200 OK
{
  "status": "success",
  "threshold": 5
}
```

### Clear All Alerts
```
POST /api/clear_alerts
Content-Type: application/json

Response: 200 OK
{
  "status": "success",
  "message": "Alerts cleared"
}
```

---

## System Health & Status

### Health Check
```
GET /health

Response: 200 OK
{
  "status": "healthy",
  "timestamp": "2024-03-17T12:30:45.123456",
  "monitoring": true
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "error": "Invalid parameter",
  "message": "Camera ID must be between 0 and 10"
}
```

### 404 Not Found
```json
{
  "error": "Resource not found",
  "message": "Incident with ID 999 not found"
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal server error",
  "message": "An unexpected error occurred"
}
```

---

## Response Status Codes

| Code | Meaning |
|------|---------|
| 200 | OK - Request successful |
| 201 | Created - Resource created |
| 400 | Bad Request - Invalid parameters |
| 401 | Unauthorized - Authentication required |
| 403 | Forbidden - Access denied |
| 404 | Not Found - Resource not found |
| 500 | Internal Server Error - Server error |

---

## Rate Limiting

Currently no rate limiting. Implement rate limiting for production:
- 100 requests per minute per IP
- 1000 requests per hour per IP

---

## Example Requests

### Python
```python
import requests

# Start monitoring
response = requests.post('http://localhost:5000/api/start_monitoring')
print(response.json())

# Get statistics
response = requests.get('http://localhost:5000/api/statistics')
stats = response.json()
print(f"Safety Score: {stats['safety_score']}")

# Get recent incidents
response = requests.get('http://localhost:5000/api/incidents?limit=10')
incidents = response.json()
for incident in incidents['incidents']:
    print(f"{incident['timestamp']}: {incident['type']}")
```

### JavaScript/Fetch
```javascript
// Start monitoring
fetch('http://localhost:5000/api/start_monitoring', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'}
})
.then(r => r.json())
.then(data => console.log(data));

// Get statistics
fetch('http://localhost:5000/api/statistics')
.then(r => r.json())
.then(stats => console.log(`Safety Score: ${stats.safety_score}`));
```

### cURL
```bash
# Start monitoring
curl -X POST http://localhost:5000/api/start_monitoring

# Get statistics
curl http://localhost:5000/api/statistics

# Get incidents
curl "http://localhost:5000/api/incidents?limit=10"

# Clear alerts
curl -X POST http://localhost:5000/api/clear_alerts
```

---

## WebSocket Events (Future Enhancement)

Planned real-time updates via WebSocket:
- Detection events
- Alert triggers
- System status changes
- Statistics updates

---

## Webhook Support (Future Enhancement)

Planned webhook notifications to external services:
- High severity incident alerts
- System status changes
- Daily reports
- Custom events

---

## Data Models

### Incident Model
```
{
  "id": integer,
  "incident_type": string,
  "severity": "LOW" | "MEDIUM" | "HIGH",
  "timestamp": ISO 8601 datetime,
  "location": string (optional),
  "worker_id": string (optional),
  "details": JSON object,
  "resolved": boolean
}
```

### Alert Model
```
{
  "id": integer,
  "alert_type": string,
  "message": string,
  "timestamp": ISO 8601 datetime,
  "is_active": boolean,
  "acknowledged_by": string (optional),
  "acknowledged_at": ISO 8601 datetime (optional)
}
```

### Statistics Model
```
{
  "total_incidents": integer,
  "today_incidents": integer,
  "high_severity": integer,
  "safety_score": float (0-100),
  "monitoring_status": "Active" | "Inactive"
}
```

---

## Batch Operations (Future Enhancement)

### Get Multiple Incidents (Batch)
```
POST /api/incidents/batch
Content-Type: application/json

Request:
{
  "ids": [1, 2, 3, 4, 5]
}

Response:
{
  "incidents": [...]
}
```

---

## Pagination

### Get Incidents with Pagination
```
GET /api/incidents?page=1&per_page=20

Query Parameters:
  page: Page number (default: 1)
  per_page: Items per page (default: 50, max: 100)

Response:
{
  "incidents": [...],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 125,
    "pages": 7
  }
}
```

---

## Version Information

**API Version**: 1.0.0
**Last Updated**: March 2024
**Compatibility**: v1.0.0+
