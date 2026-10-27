# User Registration & Login System Documentation

## Overview

The AI Safety Monitoring System now includes a secure, enterprise-grade authentication system with user registration, login, and session management. This system protects user data and ensures only authorized personnel can access the monitoring system.

## Features

### ✅ User Registration
- Self-registration for new users
- Email verification and validation
- Password strength enforcement
- Account activation
- User profile setup

### ✅ User Login
- Secure credential verification
- JWT token-based authentication
- Automatic session management
- "Remember Me" functionality
- Last login tracking

### ✅ Security Features
- **Password Hashing**: Passwords are hashed using PBKDF2-SHA256
- **JWT Tokens**: Secure token-based authentication with:
  - 1-hour access token expiration
  - 30-day refresh token expiration
- **Password Requirements**:
  - Minimum 8 characters
  - At least one uppercase letter
  - At least one lowercase letter
  - At least one digit
  - At least one special character (!@#$%^&*(),.?":{}|<>)
- **Session Management**: IP-based session validation
- **Account Security**: Account can be deactivated

## Accessing the Authentication System

### Registration Page
```
http://localhost:5000/auth
http://localhost:5000/register
```

### Login Page
```
http://localhost:5000/login
```

## Registration Process

### Step 1: Open Registration Page
Navigate to `http://localhost:5000/register` or click "Register" tab on the auth page.

### Step 2: Fill Registration Form
- **First Name** (optional): Your first name
- **Last Name** (optional): Your last name
- **Username** (required): Minimum 3 characters, unique
- **Email** (required): Valid email address, unique
- **Password** (required): Must meet strength requirements
- **Confirm Password** (required): Must match password

### Step 3: Accept Terms
Check the "I agree to the Terms of Service" checkbox.

### Step 4: Submit
Click "Create Account" button.

### Step 5: Login
Once registration is successful, login with your credentials.

## Login Process

### Step 1: Navigate to Login
Go to `http://localhost:5000/login`

### Step 2: Enter Credentials
- **Username**: Your registered username
- **Password**: Your password

### Step 3: Optional Settings
- Check "Remember me" to save username for next time

### Step 4: Submit
Click "Login" button.

### Step 5: Access Dashboard
Upon successful login, you'll be redirected to the dashboard at `http://localhost:5000/dashboard`

## API Endpoints

### 1. User Registration
```
POST /api/auth/register
Content-Type: application/json

{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "SecurePass123!",
  "confirm_password": "SecurePass123!",
  "first_name": "John",
  "last_name": "Doe"
}

Response (201 Created):
{
  "success": true,
  "message": "Registration successful! Please login with your credentials.",
  "user": {
    "user_id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "operator"
  }
}
```

### 2. User Login
```
POST /api/auth/login
Content-Type: application/json

{
  "username": "john_doe",
  "password": "SecurePass123!"
}

Response (200 OK):
{
  "success": true,
  "message": "Login successful",
  "user": {
    "user_id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "operator"
  },
  "tokens": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "Bearer",
    "expires_in": 3600
  },
  "session_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### 3. Logout
```
POST /api/auth/logout
Authorization: Bearer <access_token>

Response (200 OK):
{
  "success": true,
  "message": "Logout successful"
}
```

### 4. Get Current User
```
GET /api/auth/me
Authorization: Bearer <access_token>

Response (200 OK):
{
  "success": true,
  "user": {
    "user_id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "operator",
    "department": null,
    "is_active": true,
    "created_at": "2026-03-18T15:06:12.000000",
    "last_login": "2026-03-18T15:10:45.000000"
  }
}
```

### 5. Change Password
```
POST /api/auth/change-password
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "current_password": "SecurePass123!",
  "new_password": "NewPass456#",
  "confirm_password": "NewPass456#"
}

Response (200 OK):
{
  "success": true,
  "message": "Password changed successfully"
}
```

### 6. Refresh Access Token
```
POST /api/auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}

Response (200 OK):
{
  "success": true,
  "message": "Token refreshed successfully",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 3600
}
```

### 7. Validate Token
```
GET /api/auth/validate
Authorization: Bearer <access_token>

Response (200 OK):
{
  "success": true,
  "message": "Token is valid",
  "valid": true,
  "user": {
    "user_id": 1,
    "username": "john_doe",
    "role": "operator"
  }
}
```

### 8. Get User Sessions
```
GET /api/auth/sessions
Authorization: Bearer <access_token>

Response (200 OK):
{
  "success": true,
  "session_count": 1,
  "sessions": ["550e8400-e29b-41d4-a716-446655440000"]
}
```

## Authentication in API Requests

### Including Access Token in Requests

All protected endpoints require the access token in the Authorization header:

```
Authorization: Bearer <access_token>
```

### JavaScript Example
```javascript
// Store tokens after login
const accessToken = data.tokens.access_token;
const refreshToken = data.tokens.refresh_token;

localStorage.setItem('access_token', accessToken);
localStorage.setItem('refresh_token', refreshToken);

// Use token in API requests
fetch('/api/incidents', {
  method: 'GET',
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
    'Content-Type': 'application/json'
  }
})
```

### cURL Example
```bash
curl -X GET http://localhost:5000/api/incidents \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json"
```

### Python Example
```python
import requests

access_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

headers = {
    'Authorization': f'Bearer {access_token}',
    'Content-Type': 'application/json'
}

response = requests.get('http://localhost:5000/api/incidents', headers=headers)
print(response.json())
```

## User Roles & Permissions

### Role: Admin
- User management
- System settings
- Report generation
- Incident management
- Camera configuration
- Data export
- Audit log access
- Shift management
- Alert configuration

### Role: Supervisor
- Report generation
- Incident management
- Data export
- Audit log access
- Shift management
- Alert configuration

### Role: Operator (Default)
- Incident management

## Security Best Practices

### For Users
1. **Strong Passwords**: Use the password strength indicator
2. **Keep Tokens Safe**: Never share your access tokens
3. **Logout When Done**: Always logout when finished
4. **Use HTTPS**: Always access the system over HTTPS in production
5. **Remember Me**: Only use on secure, personal devices

### For Administrators
1. **Secure Configuration**: Set strong `SECRET_KEY` in config
2. **HTTPS Only**: Deploy with HTTPS in production
3. **Token Expiration**: Configure appropriate token expiration times
4. **Session Timeout**: Configure session idle timeout
5. **Audit Logs**: Monitor login/logout activities
6. **Account Security**: Deactivate unused accounts

## Configuration

Edit `backend/config/settings.py`:

```python
# JWT Configuration
JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1 hour
JWT_REFRESH_TOKEN_EXPIRES = 2592000  # 30 days

# Security
SECRET_KEY = 'your-very-secure-secret-key-change-in-production'
```

## Troubleshooting

### "Invalid username or password"
- Verify username/password are correct
- Check that account is active (not deactivated)
- Try resetting password if forgotten

### "Username already exists"
- Choose a different username
- Username must be unique

### "Email already registered"
- Use a different email address
- If it's your email, login instead

### "Password does not meet requirements"
- Minimum 8 characters
- Include uppercase letter (A-Z)
- Include lowercase letter (a-z)
- Include digit (0-9)
- Include special character (!@#$%^&*(),.?":{}|<>)

### "Token expired"
- Use refresh token to get new access token
- Or login again

### "Invalid or expired token"
- Token has expired or is malformed
- Login again to get new tokens

## Error Codes

| Status | Code | Message |
|--------|------|---------|
| 400 | Bad Request | Missing required fields |
| 401 | Unauthorized | Invalid credentials or token |
| 403 | Forbidden | Account inactive or unauthorized access |
| 404 | Not Found | User not found |
| 409 | Conflict | Username or email already exists |
| 500 | Server Error | Internal server error |

## Database Schema

### Users Table
```sql
CREATE TABLE users (
  id INTEGER PRIMARY KEY,
  username VARCHAR(120) UNIQUE NOT NULL,
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  first_name VARCHAR(120),
  last_name VARCHAR(120),
  role VARCHAR(50) DEFAULT 'operator',
  department VARCHAR(120),
  is_active BOOLEAN DEFAULT True,
  last_login DATETIME,
  created_at DATETIME,
  updated_at DATETIME,
  INDEX(username),
  INDEX(email)
);
```

## Session Management

Sessions are stored in memory with the following details:
- **Session ID**: UUID
- **User ID**: Integer
- **Token**: JWT access token
- **IP Address**: For security verification
- **Created At**: Session creation timestamp
- **Last Activity**: Last request timestamp
- **Timeout**: 30 minutes of inactivity

## What's Included in This Update

✅ **auth.html**: Beautiful, responsive login/registration UI
✅ **Secure Registration Endpoint**: Full validation and database integration
✅ **Secure Login Endpoint**: Credential verification with password hashing
✅ **Password Security**: PBKDF2-SHA256 hashing + strength requirements
✅ **JWT Tokens**: Access & refresh token system
✅ **Session Management**: IP-based session validation
✅ **User Profile**: Extended user information retrieval
✅ **Password Change**: Secure password update functionality
✅ **Token Refresh**: Renew expired tokens without re-login
✅ **Token Validation**: Verify token status
✅ **Logout**: Secure session termination
✅ **Error Handling**: Comprehensive error messages
✅ **Frontend Routes**: Auth page integrated with Flask

## Testing the Authentication System

### Quick Test
```bash
# Register a user
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "TestPass123!",
    "confirm_password": "TestPass123!",
    "first_name": "Test",
    "last_name": "User"
  }'

# Login with the registered user
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "TestPass123!"
  }'

# Use the access_token from login response
ACCESS_TOKEN="<your-token-here>"

# Get user info
curl -X GET http://localhost:5000/api/auth/me \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review error messages carefully
3. Check logs at: `backend/logs/`
4. Ensure database is initialized: `python -c "from backend.database import init_db; init_db()"`

---

**System Version**: 2.0 with Secure Authentication
**Last Updated**: March 18, 2026
