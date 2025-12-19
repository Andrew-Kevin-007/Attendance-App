"""
Download OpenCV DNN Face Detection Models
This script downloads pre-trained models for better face detection accuracy.
"""
import urllib.request
import os
import sys

MODEL_URL = "https://github.com/opencv/opencv_3rdparty/raw/dnn_samples_face_detector_20170830/res10_300x300_ssd_iter_140000.caffemodel"
CONFIG_URL = "https://raw.githubusercontent.com/opencv/opencv/master/samples/dnn/face_detector/deploy.prototxt"

MODEL_FILE = "res10_300x300_ssd_iter_140000.caffemodel"
CONFIG_FILE = "deploy.prototxt"

def download_file(url, filename):
    """Download file with progress"""
    try:
        print(f"Downloading {filename}...")
        
        def reporthook(count, block_size, total_size):
            percent = int(count * block_size * 100 / total_size)
            sys.stdout.write(f"\r{percent}%")
            sys.stdout.flush()
        
        urllib.request.urlretrieve(url, filename, reporthook)
        print(f"\n✓ {filename} downloaded successfully")
        return True
    except Exception as e:
        print(f"\n✗ Failed to download {filename}: {e}")
        return False

def main():
    """Download DNN models for improved face detection"""
    print("=" * 60)
    print("OpenCV DNN Face Detection Model Downloader")
    print("=" * 60)
    print("\nThese models provide better accuracy than Haar Cascades.")
    print("Model size: ~10MB\n")
    
    success = True
    
    # Check if files already exist
    if os.path.exists(MODEL_FILE):
        print(f"✓ {MODEL_FILE} already exists")
    else:
        success = download_file(MODEL_URL, MODEL_FILE) and success
    
    if os.path.exists(CONFIG_FILE):
        print(f"✓ {CONFIG_FILE} already exists")
    else:
        success = download_file(CONFIG_URL, CONFIG_FILE) and success
    
    print("\n" + "=" * 60)
    if success:
        print("✓ All models downloaded successfully!")
        print("\nThe face recognition system will now use DNN models")
        print("for improved accuracy and better detection.")
    else:
        print("⚠ Some models failed to download.")
        print("The system will fall back to Haar Cascades.")
    print("=" * 60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nDownload cancelled by user.")
        sys.exit(1)
