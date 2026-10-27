import requests
import time

# Give server a moment to start if needed
time.sleep(1)

# Test if video_feed endpoint is working
print("Testing /video_feed endpoint...")
try:
    response = requests.head('http://localhost:5000/video_feed', timeout=5)
    print(f"Status Code: {response.status_code}")
    print(f"Content-Type: {response.headers.get('Content-Type', 'Not Found')}")
    
    if response.status_code == 200:
        print("✅ Video stream endpoint is working!")
    else:
        print("❌ Video stream endpoint returned an error")
except Exception as e:
    print(f"❌ Error connecting to server: {e}")
    print("Make sure the Flask server is running!")
