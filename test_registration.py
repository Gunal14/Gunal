#!/usr/bin/env python
"""Test registration endpoint"""
import requests
import json

BASE_URL = "http://localhost:5000"

def test_register():
    """Test user registration"""
    data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "StrongPass123!",
        "confirm_password": "StrongPass123!",
        "first_name": "Test",
        "last_name": "User"
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/register", json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    return response.json()

if __name__ == "__main__":
    try:
        result = test_register()
        print("\n✓ Registration test completed")
    except Exception as e:
        print(f"\n✗ Error: {e}")
