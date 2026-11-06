import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_unified_quality_check():
    print("\n🚀 Testing Endpoint: POST /api/v1/unified-quality-check...")
    url = f"{BASE_URL}/api/v1/unified-quality-check"
    
    try:
        # Using PIL to generate real, valid image bytes so OpenCV doesn't crash
        from PIL import Image as PILImage
        import io

        img = PILImage.new('RGB', (100, 100), color = 'white')
        
        master_bytes = io.BytesIO()
        sample_bytes = io.BytesIO()
        img.save(master_bytes, format='PNG')
        img.save(sample_bytes, format='PNG')
        
        master_bytes.seek(0)
        sample_bytes.seek(0)
        
        files = {
            "master_file": ("dummy_master.png", master_bytes, "image/png"),
            "production_file": ("dummy_sample.png", sample_bytes, "image/png")
        }
        data = {
            "expected_barcode": "1234567890"
        }
        
        response = requests.post(url, files=files, data=data)
        
        print(f"📡 Status Code: {response.status_code}")
        if response.status_code == 200:
            print("✅ Success! Nested JSON Payload Received From Pipeline Structure:")
            print(json.dumps(response.json(), indent=2))
            return response.json()["inspection_details"]["id"]
        else:
            print(f"❌ Failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Connection Error: Is your Uvicorn app currently running? Details: {e}")
        return None

def test_history_endpoint():
    print("\n🚀 Testing Endpoint: GET /api/v1/history...")
    url = f"{BASE_URL}/api/v1/history"
    
    response = requests.get(url)
    print(f"📡 Status Code: {response.status_code}")
    if response.status_code == 200:
        print("✅ History records fetched successfully:")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"❌ Failed: {response.text}")

def test_single_lookup(inspection_id):
    if not inspection_id:
        print("\n⚠️ Skipping single inspection lookup test because no ID was generated.")
        return
        
    print(f"\n🚀 Testing Endpoint: GET /api/v1/inspection/{inspection_id}...")
    url = f"{BASE_URL}/api/v1/inspection/{inspection_id}"
    
    response = requests.get(url)
    print(f"📡 Status Code: {response.status_code}")
    if response.status_code == 200:
        print(f"✅ Deep nested audit log parsed successfully for ID [{inspection_id}]:")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"❌ Failed: {response.text}")
def test_single_image_extraction():
    print("\n🚀 Testing Endpoint: POST /upload-image/ (Standalone Extraction)...")
    url = f"{BASE_URL}/upload-image/"
    
    try:
        from PIL import Image as PILImage
        import io

        # Generate a mock valid image asset
        img = PILImage.new('RGB', (150, 150), color = 'blue')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        files = {
            "file": ("standalone_test.png", img_bytes, "image/png")
        }
        
        response = requests.post(url, files=files)
        
        print(f"📡 Status Code: {response.status_code}")
        if response.status_code == 200:
            print("✅ Success! Single-Image Structured Enterprise Response Received:")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"❌ Failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Connection Error: Is your Uvicorn app running? Details: {e}")

if __name__ == "__main__":
    # 1. Run the primary quality pipeline evaluation check
    generated_id = test_unified_quality_check()
    
    # 2. Run the overview timeline list query
    test_history_endpoint()
    
    # 3. Drill down into the specific details of the item we just processed
    test_single_lookup(generated_id)
    
    # 4. RUN THE BRAND NEW SINGLE IMAGE EXTRACTOR TEST
    test_single_image_extraction()
    