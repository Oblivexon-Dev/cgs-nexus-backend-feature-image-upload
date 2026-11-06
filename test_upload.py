import requests
import json

# The URL of your locally running FastAPI server
url = "http://127.0.0.1:8000/upload-image/"

# Path to the image you want to test
image_path = "backend model test image 8.jpg" 

# Form data configurations mapping to your boolean parameters
data = {
    "extract_logo": "true",
    "extract_text": "true"
}

try:
    with open(image_path, "rb") as image_file:
        files = {"file": (image_path, image_file, "image/jpeg")}
        
        print(f"🚀 Sending request to {url}...")
        response = requests.post(url, data=data, files=files)
        
        if response.status_code == 200:
            result_json = response.json()
            print("\n✅ Execution Successful! Server Response Summary:")
            print("--------------------------------------------------")
            print(f"File Processed: {result_json.get('file_processed')}")
            print(f"Document Type: {result_json.get('document_type')}")
            print(f"Processing Time: {result_json['metadata']['processing_time_seconds']}s")
            
            # Print Logo Extraction URL
            logo_info = result_json.get("logo_analysis")
            if logo_info and logo_info.get("logo_detected"):
                print(f"\n🎨 Logo Detected: {logo_info.get('brand_name')}")
                print(f"🔗 Clean Matte Logo URL: {logo_info.get('logo_url')}")
            else:
                print("\n❌ No logo detected by the vision engine.")
                
            # Print a snippet of extracted typography JSON for layout confirmation
            print(f"\n📝 Typography Extractions Found: {len(result_json.get('styled_elements', []))} blocks.")
            if result_json.get("styled_elements"):
                print("\nFirst Extracted Text Block JSON Structure Sample:")
                print(json.dumps(result_json["styled_elements"][0], indent=2))
                
        else:
            print(f"❌ Server returned error code {response.status_code}: {response.text}")

except FileNotFoundError:
    print(f"❌ Error: Could not find the test image file at '{image_path}'. Check your file name!")
except requests.exceptions.ConnectionError:
    print("❌ Error: Could not connect to the server. Make sure main.py is running on port 8000!")