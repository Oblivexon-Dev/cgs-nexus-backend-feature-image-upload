import os
import cv2
import numpy as np
from pdf2image import convert_from_path

class PrepressQualityPipeline:
    def __init__(self, dpi=200):
        self.dpi = dpi

    def load_file(self, file_path):
        """
        [File Gatekeeper] Detects extension and converts PDFs or 
        loads JPEGs directly into standard image matrices.
        """
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext in ['.jpg', '.jpeg', '.png']:
            print(f"📸 Loading image directly: {os.path.basename(file_path)}")
            img = cv2.imread(file_path)
            if img is None:
                raise FileNotFoundError(f"Could not open image path: {file_path}")
            return img
            
        elif ext == '.pdf':
            print(f"📄 Unpacking PDF vector formatting: {os.path.basename(file_path)}")
            try:
                pages = convert_from_path(file_path, dpi=self.dpi)
                if not pages:
                    raise ValueError("Target PDF layout contains no readable layers.")
                # Turn first page into standard RGB array, then swap to OpenCV BGR color format
                pil_img = pages[0].convert('RGB')
                return cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
            except Exception as e:
                print(f"❌ PDF processing failed: {e}")
                return None
        else:
            print(f"❌ Extension '{ext}' is unmapped in this gatekeeper version.")
            return None

    def align_production_to_master(self, master_img, production_img):
        """
        [Auto-Alignment Engine] Detects visual landmarks using feature descriptors
        to map the production file perfectly flush over the approved template.
        """
        print("🔍 Aligning production file landmarks to master templates...")
        
        # Convert matrix spaces to grayscale for algorithmic point-matching
        gray_master = cv2.cvtColor(master_img, cv2.COLOR_BGR2GRAY)
        gray_prod = cv2.cvtColor(production_img, cv2.COLOR_BGR2GRAY)

        # Generate spatial landmarks using ORB (Oriented FAST and Rotated BRIEF)
        orb = cv2.ORB_create(nfeatures=2000)
        kp_master, des_master = orb.detectAndCompute(gray_master, None)
        kp_prod, des_prod = orb.detectAndCompute(gray_prod, None)

        if des_master is None or des_prod is None:
            print("⚠️ Insufficient details found. Defaulting to standard dimension scaling.")
            return cv2.resize(production_img, (master_img.shape[1], master_img.shape[0]))

        # Track similarities using standard Hamming distance
        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        matches = bf.match(des_master, des_prod)
        matches = sorted(matches, key=lambda x: x.distance)

        good_matches = matches[:100]
        if len(good_matches) < 4:
            print("⚠️ Landmark mapping failed due to lack of reference points. Resizing instead.")
            return cv2.resize(production_img, (master_img.shape[1], master_img.shape[0]))

        src_pts = np.float32([kp_master[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
        dst_pts = np.float32([kp_prod[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)

        # Warp structural layout perspective
        H, _ = cv2.findHomography(dst_pts, src_pts, cv2.RANSAC, 5.0)
        h, w, c = master_img.shape
        return cv2.warpPerspective(production_img, H, (w, h))

    def scan_for_barcodes(self, img):
        """
        [Data Integrity Layer] Translates printed lines into readable string numbers
        using OpenCV's built-in native engine.
        """
        print("📊 Scanning design canvas for tracking data (Barcodes)...")
        payloads = []
        try:
            detector = cv2.barcode.BarcodeDetector()
            # Catching the output dynamically handles both 3-value and 4-value OpenCV versions cleanly
            outputs = detector.detectAndDecode(img)
            retval = outputs[0]
            decoded_info = outputs[1]
            decoded_type = outputs[2]
            
            if retval and decoded_info:
                for info, btype in zip(decoded_info, decoded_type):
                    if info: 
                        payloads.append({"type": str(btype), "payload": str(info)})
                        print(f"   └─ Found Barcode: {info}")
        except Exception as e:
            print(f"⚠️ Native barcode scan bypassed: {e}")
            
        return payloads

    def evaluate_visual_changes(self, master_img, aligned_prod_img, deviation_tolerance=20):
        """
        [Visual Delta Engine] Compares pixel values channel by channel to catch
        shifts, changes, or brand-color distortions.
        """
        print("📐 Computing absolute pixel subtraction matrix...")
        
        # Absolute matrix difference extraction
        diff = cv2.absdiff(master_img, aligned_prod_img)
        gray_diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
        
        # Enforce threshold limit to drop anti-aliasing rendering artifacts
        _, threshold_mask = cv2.threshold(gray_diff, deviation_tolerance, 255, cv2.THRESH_BINARY)
        
        # Compute exact percentage metrics
        mismatched_pixel_count = np.sum(threshold_mask == 255)
        total_pixel_grid = threshold_mask.size
        variance_rate = (mismatched_pixel_count / total_pixel_grid) * 100
        
        # Create user evaluation canvas overlay: Paint changed pixels bright Red
        heatmap_canvas = master_img.copy()
        heatmap_canvas[threshold_mask == 255] = [0, 0, 255]
        
        return heatmap_canvas, variance_rate

    def process_quality_check(self, master_path, production_path, heatmap_output_path=None, expected_barcode=None):
        """Coordinates the entire processing pipeline sequence."""
        # 1. Load/Decode
        master = self.load_file(master_path)
        production = self.load_file(production_path)
        
        if master is None or production is None:
            return {"status": "Error", "message": "Failed to compile file matrices."}

        # 2. Alignment Overlay
        aligned_production = self.align_production_to_master(master, production)
        
        # 3. Barcode String Evaluation
        barcodes = self.scan_for_barcodes(aligned_production)
        barcode_ok = True
        if expected_barcode:
            barcode_ok = any(b['payload'] == expected_barcode for b in barcodes)

        # 4. Difference Map Calculation
        heatmap, variance = self.evaluate_visual_changes(master, aligned_production)
        
        # Save the heatmap canvas locally if an explicit path is provided
        if heatmap_output_path:
            cv2.imwrite(heatmap_output_path, heatmap)
            print(f"💾 Heatmap persistent layer written to: {heatmap_output_path}")
        
        # Final Decision Threshold Gate
        is_passed = variance < 0.5 and barcode_ok
        
        return {
            "is_passed": is_passed,
            "variance_percentage": variance,
            "barcodes_detected": barcodes,
            "barcode_match": barcode_ok if expected_barcode else "Not Checked",
            "heatmap_image": heatmap,
            "aligned_image": aligned_production
        }

# --- TEMPORARY TEST BLOCK ---
if __name__ == "__main__":
    MASTER_TEST = "test_assets/master.jpg"
    PRODUCTION_TEST = "test_assets/sample.jpg"
    
    pipeline = PrepressQualityPipeline()
    
    print("\n🚀 Starting local pipeline test verification...")
    if os.path.exists(MASTER_TEST) and os.path.exists(PRODUCTION_TEST):
        results = pipeline.process_quality_check(MASTER_TEST, PRODUCTION_TEST, "test_assets/error_heatmap.png")
        print(f"📊 Layout Difference: {results['variance_percentage']:.2f}%")
        print(f"🔔 Verification Passed: {results['is_passed']}")
    else:
        print(f"⚠️ Test files not found! Please ensure 'master.jpg' and 'sample.jpg' are inside 'test_assets'.")