import requests

print("Testing /video_feed endpoint...")
try:
    response = requests.get('http://localhost:5000/video_feed', stream=True, timeout=5)
    print(f"Status: {response.status_code}")
    print(f"Content-Type: {response.headers.get('Content-Type')}")
    
    # Try to read first chunk
    chunk = next(response.iter_content(chunk_size=1024), None)
    if chunk:
        print(f"First chunk size: {len(chunk)} bytes")
        print(f"First 50 bytes: {chunk[:50]}")
        # Check for JPEG markers
        if b'\xff\xd8' in chunk[:100]:  # JPEG SOI marker
            print("✅ Valid JPEG data detected")
        else:
            print("❌ No JPEG data found")
    else:
        print("❌ No data received from stream")
except Exception as e:
    print(f"❌ Error: {e}")
    print("Make sure Flask server is running!")
