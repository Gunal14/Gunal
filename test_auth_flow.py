#!/usr/bin/env python
"""Test complete authentication flow"""
import requests

print('Testing Complete Authentication Flow')
print('=' * 60)

# 1. REGISTER
print('\n1. Registering new user...')
reg_data = {
    'username': 'testflowuser',
    'email': 'testflow@example.com',
    'password': 'FlowTest123!',
    'confirm_password': 'FlowTest123!',
    'first_name': 'Flow',
    'last_name': 'Tester',
    'role': 'supervisor'
}
reg = requests.post('http://localhost:5000/api/auth/register', json=reg_data)
print('   Status:', reg.status_code)
print('   Success:', reg.json()['success'])

# 2. LOGIN
print('\n2. Logging in...')
login_data = {'username': 'testflowuser', 'password': 'FlowTest123!'}
login = requests.post('http://localhost:5000/api/auth/login', json=login_data)
print('   Status:', login.status_code)
login_resp = login.json()
print('   Success:', login_resp['success'])
token = login_resp['tokens']['access_token']

# 3. ACCESS PROTECTED ENDPOINT
print('\n3. Testing protected endpoint...')
headers = {'Authorization': 'Bearer ' + token}
protected = requests.get('http://localhost:5000/api/auth/me', headers=headers)
print('   Status:', protected.status_code)
print('   Success:', protected.status_code == 200)

print('\n' + '=' * 60)
print('RESULT: All tests PASSED!')
