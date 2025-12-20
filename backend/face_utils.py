import numpy as np
import cv2
import pickle
import os

# Load DNN face detector (better than Haar Cascades)
MODEL_FILE = "res10_300x300_ssd_iter_140000.caffemodel"
CONFIG_FILE = "deploy.prototxt"

# Check if models exist, otherwise use Haar Cascade as fallback
if os.path.exists(MODEL_FILE) and os.path.exists(CONFIG_FILE):
    try:
        face_net = cv2.dnn.readNetFromCaffe(CONFIG_FILE, MODEL_FILE)
        use_dnn = True
        print("✓ Using DNN face detector (High Accuracy)")
    except Exception as e:
        print(f"⚠ Could not load DNN models: {e}")
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')  # type: ignore
        use_dnn = False
        print("✓ Using Haar Cascade detector (Fallback)")
else:
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')  # type: ignore
    use_dnn = False
    print("✓ Using Haar Cascade detector (Run download_models.py for better accuracy)")

# Load eye cascade for liveness detection
eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')  # type: ignore

def detect_faces_dnn(frame, conf_threshold=0.5):
    """Detect faces using DNN model (more accurate than Haar Cascade)"""
    (h, w) = frame.shape[:2]
    blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 1.0,
                                 (300, 300), (104.0, 177.0, 123.0))
    
    face_net.setInput(blob)
    detections = face_net.forward()
    
    faces = []
    for i in range(0, detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        
        if confidence > conf_threshold:
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            (x, y, x2, y2) = box.astype("int")
            # Ensure coordinates are within frame bounds
            x, y = max(0, x), max(0, y)
            x2, y2 = min(w, x2), min(h, y2)
            faces.append((x, y, x2-x, y2-y))
    
    return faces

def compute_lbp(image, radius=1):
    """Compute Local Binary Pattern for texture analysis"""
    lbp_image = np.zeros_like(image)
    
    for i in range(radius, image.shape[0] - radius):
        for j in range(radius, image.shape[1] - radius):
            center = image[i, j]
            
            # 8 surrounding pixels
            pixels = [
                image[i-radius, j-radius], image[i-radius, j], image[i-radius, j+radius],
                image[i, j+radius], image[i+radius, j+radius], image[i+radius, j],
                image[i+radius, j-radius], image[i, j-radius]
            ]
            
            binary_value = 0
            for idx, pixel in enumerate(pixels):
                if pixel >= center:
                    binary_value |= (1 << idx)
            
            lbp_image[i, j] = binary_value
    
    return lbp_image

def create_enhanced_encoding(face_region):
    """Create robust face encoding using multiple OpenCV techniques"""
    face_resized = cv2.resize(face_region, (128, 128))
    gray_face = cv2.cvtColor(face_resized, cv2.COLOR_BGR2GRAY)
    
    # 1. Color histograms (LAB color space - better than RGB)
    lab = cv2.cvtColor(face_resized, cv2.COLOR_BGR2LAB)
    hist_l = cv2.calcHist([lab], [0], None, [32], [0, 256])
    hist_a = cv2.calcHist([lab], [1], None, [32], [0, 256])
    hist_b = cv2.calcHist([lab], [2], None, [32], [0, 256])
    
    hist_l = cv2.normalize(hist_l, hist_l).flatten()
    hist_a = cv2.normalize(hist_a, hist_a).flatten()
    hist_b = cv2.normalize(hist_b, hist_b).flatten()
    
    # 2. HOG features (Histogram of Oriented Gradients)
    hog = cv2.HOGDescriptor((128, 128), (16, 16), (8, 8), (8, 8), 9)
    hog_features = hog.compute(gray_face)
    hog_features = np.array(hog_features).flatten()[:128]
    
    # 3. LBP (Local Binary Patterns) - texture features
    lbp = compute_lbp(gray_face)
    lbp_hist = cv2.calcHist([lbp], [0], None, [32], [0, 256])
    lbp_hist = cv2.normalize(lbp_hist, lbp_hist).flatten()
    
    # 4. Edge features
    edges = cv2.Canny(gray_face, 100, 200)
    edge_hist = cv2.calcHist([edges], [0], None, [16], [0, 256])
    edge_hist = cv2.normalize(edge_hist, edge_hist).flatten()
    
    # Combine all features
    encoding = np.concatenate([
        hist_l,        # 32 features
        hist_a,        # 32 features
        hist_b,        # 32 features
        hog_features,  # 128 features
        lbp_hist,      # 32 features
        edge_hist      # 16 features
    ])
    
    return encoding

def get_face_encoding(frame):
    """Extract face encoding from frame with quality checks"""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Use DNN if available, otherwise Haar Cascade
    if use_dnn:
        faces = detect_faces_dnn(frame)
    else:
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(50, 50))
    
    if len(faces) == 0:
        return None, ["No face detected"]
    
    if len(faces) > 1:
        return None, ["Multiple faces detected. Please ensure only one person is in frame"]
    
    # Get face region
    x, y, w, h = faces[0]
    face_region = frame[y:y+h, x:x+w]
    
    # Check face quality
    quality_issues = check_face_quality(face_region)
    if quality_issues:
        return None, quality_issues
    
    # Check liveness (basic anti-spoofing)
    is_live, liveness_msg = detect_basic_liveness(frame, (x, y, w, h))
    if not is_live:
        return None, [liveness_msg]
    
    # Create enhanced face encoding
    encoding = create_enhanced_encoding(face_region)
    
    return encoding, []

def check_face_quality(face_img):
    """Check if face image quality is good enough for recognition"""
    issues = []
    
    # Check face size (should be at least 60x60 pixels - more lenient)
    if face_img.shape[0] < 60 or face_img.shape[1] < 60:
        issues.append("Face too small. Please move closer to the camera")
    
    # Check brightness
    gray = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY)
    brightness = np.mean(gray)
    if brightness < 30:
        issues.append("Image too dark. Please improve lighting")
    elif brightness > 240:
        issues.append("Image too bright. Please reduce lighting")
    
    # Check blur using Laplacian variance (more lenient threshold)
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    if laplacian_var < 30:
        issues.append("Image is blurry. Please hold camera steady")
    
    return issues

def detect_basic_liveness(frame, face_coords):
    """Basic liveness detection - simplified for better usability"""
    x, y, w, h = face_coords
    face_region = frame[y:y+h, x:x+w]
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray_face = gray[y:y+h, x:x+w]
    
    # 1. Check image sharpness (photos on screens have unusual sharpness)
    laplacian_var = cv2.Laplacian(gray_face, cv2.CV_64F).var()
    if laplacian_var > 3000:
        return False, "Image quality suspicious. Please use direct camera capture"
    
    # 2. Color distribution check (photos have different color distribution)
    color_std = np.std(face_region, axis=(0, 1))
    if np.mean(color_std) < 3:
        return False, "Color distribution suspicious"
    
    return True, ""

def compare_faces(known_encoding, unknown_encoding, tolerance=0.5):
    """Compare two face encodings and return match status with confidence
    
    Args:
        tolerance: Higher = more lenient (0.5 = 50% confidence required)
    """
    # Calculate multiple distance metrics for robust matching
    
    # 1. Euclidean distance (L2 norm)
    euclidean_dist = np.linalg.norm(known_encoding - unknown_encoding)
    
    # 2. Cosine similarity (best for normalized vectors)
    cosine_sim = np.dot(known_encoding, unknown_encoding) / (
        np.linalg.norm(known_encoding) * np.linalg.norm(unknown_encoding) + 1e-10
    )
    
    # 3. Manhattan distance (L1 norm - less sensitive to outliers)
    manhattan_dist = np.sum(np.abs(known_encoding - unknown_encoding))
    
    # 4. Correlation coefficient
    corr = np.corrcoef(known_encoding, unknown_encoding)[0, 1]
    
    # Normalize distances to 0-1 range (with better scaling)
    euclidean_normalized = 1.0 / (1.0 + euclidean_dist / 100.0)  # Adjusted scaling
    manhattan_normalized = 1.0 / (1.0 + manhattan_dist / 1000.0)  # Adjusted scaling
    
    # Combined confidence score (weighted average favoring cosine similarity)
    confidence = float(
        0.35 * euclidean_normalized +
        0.40 * cosine_sim +
        0.15 * manhattan_normalized +
        0.10 * corr
    )
    
    # Ensure confidence is in valid range
    confidence = max(0.0, min(1.0, confidence))
    
    # Match if confidence is above threshold
    match = confidence >= (1.0 - tolerance)
    
    return match, confidence


def compare_faces_multi(known_encodings, unknown_encoding, tolerance=0.5):
    """Compare unknown face against multiple known encodings
    
    Uses best match and average confidence from all samples for better accuracy.
    """
    if not known_encodings:
        return False, 0.0
    
    confidences = []
    for known_enc in known_encodings:
        _, conf = compare_faces(known_enc, unknown_encoding, tolerance)
        confidences.append(conf)
    
    # Use maximum confidence (best match)
    best_confidence = max(confidences)
    
    # Also consider average confidence for consistency
    avg_confidence = np.mean(confidences)
    
    # Final confidence: weighted combination
    final_confidence = 0.7 * best_confidence + 0.3 * avg_confidence
    
    # Match if best confidence exceeds threshold
    match = best_confidence >= (1.0 - tolerance)
    
    return match, float(final_confidence)

def encoding_to_bytes(encoding):
    """Convert numpy array to bytes for database storage"""
    return pickle.dumps(encoding)

def bytes_to_encoding(encoding_bytes):
    """Convert bytes back to numpy array"""
    return pickle.loads(encoding_bytes)
