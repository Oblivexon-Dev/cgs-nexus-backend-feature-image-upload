import os
import requests
import json

BASE_URL = "http://127.0.0.1:8000"
ENDPOINT_URL = f"{BASE_URL}/upload-image/"

# List out your exact test image filenames present in your working folder
TEST_IMAGES = [
    "backend model test image 12.jpg",  # Bingo Logo # Purple Mandala Logo     # Blue Abstract 'A' Logo
]

def verify_logo_pipeline():
    print("🚀 Starting Main Logo Extraction Pipeline Verification...\n")
    
    for idx, img_name in enumerate(TEST_IMAGES, 1):
        if not os.path.exists(img_name):
            print(f"⚠️ [Image {idx}] Missing file local path: '{img_name}'. Skipping...")
            continue
            
        print(f"📦 [Image {idx}] Processing file asset: '{img_name}'")
        
        try:
            with open(img_name, "rb") as file_stream:
                files = {"file": (img_name, file_stream, "image/jpeg")}
                
                # Submit POST action to local endpoint
                response = requests.post(ENDPOINT_URL, files=files)
                
            print(f"📡 API Response Status Code: {response.status_code}")
            
            if response.status_code == 200:
                response_payload = response.json()
                print("✅ Structured Data Package Retrieved:")
                print(json.dumps(response_payload, indent=2))
                
                # Verify that our physical extraction mapping successfully injected a URL path
                logo_details = response_payload.get("logo_analysis", {})
                if logo_details and logo_details.get("logo_url"):
                    print(f"🎯 Cropped Logo Public Asset Route: {BASE_URL}{logo_details['logo_url']}")
                else:
                    print("🛑 Logo tracking object was parsed, but no physical asset URL path was formed.")
            else:
                print(f"❌ Pipeline Processing Defect: {response.text}")
                
        except Exception as error:
            print(f"❌ Connection Blocked: Is your Uvicorn service alive at {BASE_URL}? Context: {error}")
            
        print("-" * 70)

if __name__ == "__main__":
    verify_logo_pipeline()