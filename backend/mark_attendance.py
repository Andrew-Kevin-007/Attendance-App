import cv2
import base64
import requests
import sys
from datetime import datetime
import numpy as np

# Initialize DNN face detector (much better than Haar Cascade)
print("Loading advanced face detection model...")
modelFile = "opencv_face_detector_uint8.pb"
configFile = "opencv_face_detector.pbtxt"

# Try DNN detector first, fallback to improved Haar Cascade if not available
try:
    net = cv2.dnn.readNetFromTensorflow(modelFile, configFile)
    use_dnn = True
    print("✅ Using DNN face detector (High Accuracy)")
except:
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')  # type: ignore
    eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')  # type: ignore
    use_dnn = False
    print("✅ Using Enhanced Haar Cascade detector (Improved)")

def detect_faces_dnn(frame, conf_threshold=0.7):
    """Detect faces using DNN model (more accurate)"""
    h, w = frame.shape[:2]
    blob = cv2.dnn.blobFromImage(frame, 1.0, (300, 300), [104, 117, 123], False, False)
    net.setInput(blob)
    detections = net.forward()
    
    faces = []
    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > conf_threshold:
            x1 = int(detections[0, 0, i, 3] * w)
            y1 = int(detections[0, 0, i, 4] * h)
            x2 = int(detections[0, 0, i, 5] * w)
            y2 = int(detections[0, 0, i, 6] * h)
            faces.append((x1, y1, x2 - x1, y2 - y1, confidence))
    return faces

def detect_faces_haar(frame):
    """Detect faces using Haar Cascade with improvements"""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Improve contrast for better detection
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    gray = clahe.apply(gray)
    
    # Detect faces with optimized parameters
    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.05,  # Smaller steps for better detection
        minNeighbors=4,     # Reduced for better sensitivity
        minSize=(80, 80),
        flags=cv2.CASCADE_SCALE_IMAGE
    )
    
    # Validate faces by checking for eyes
    validated_faces = []
    for (x, y, w, h) in faces:
        face_roi = gray[y:y+h, x:x+w]
        eyes = eye_cascade.detectMultiScale(face_roi, scaleFactor=1.1, minNeighbors=3, minSize=(20, 20))
        
        # Accept if at least one eye detected or face is large enough
        if len(eyes) >= 1 or (w > 150 and h > 150):
            validated_faces.append((x, y, w, h, 0.9))
    
    return validated_faces if validated_faces else [(x, y, w, h, 0.7) for (x, y, w, h) in faces]

class FaceTracker:
    """Smooth face tracking to reduce jitter"""
    def __init__(self, smoothing=0.7):
        self.prev_faces = []
        self.smoothing = smoothing
    
    def update(self, faces):
        if not faces:
            return faces
        
        if not self.prev_faces:
            self.prev_faces = faces
            return faces
        
        # Smooth transitions
        smoothed = []
        for face in faces:
            x, y, w, h = face[:4]
            # Find closest previous face
            if self.prev_faces:
                closest = min(self.prev_faces, key=lambda f: abs(f[0] - x) + abs(f[1] - y))
                x = int(x * (1 - self.smoothing) + closest[0] * self.smoothing)
                y = int(y * (1 - self.smoothing) + closest[1] * self.smoothing)
                w = int(w * (1 - self.smoothing) + closest[2] * self.smoothing)
                h = int(h * (1 - self.smoothing) + closest[3] * self.smoothing)
            
            if len(face) == 5:
                smoothed.append((x, y, w, h, face[4]))
            else:
                smoothed.append((x, y, w, h))
        
        self.prev_faces = smoothed
        return smoothed

tracker = FaceTracker()

print("="*60)
print("   PROFESSIONAL FACE ATTENDANCE SYSTEM")
print("="*60)
print("\nInitializing webcam...")

def draw_text_with_shadow(frame, text, pos, font, scale, color, thickness, shadow_offset=2):
    """Draw text with shadow for better visibility"""
    x, y = pos
    # Shadow
    cv2.putText(frame, text, (x + shadow_offset, y + shadow_offset), 
                font, scale, (0, 0, 0), thickness + 1)
    # Main text
    cv2.putText(frame, text, (x, y), font, scale, color, thickness)

def draw_face_guide(frame, center_x, center_y, size=200):
    """Draw a guide oval for face positioning with glow effect"""
    overlay = frame.copy()
    # Outer glow
    cv2.ellipse(overlay, (center_x, center_y), (size//2+10, int(size*0.7)+10), 0, 0, 360, (80, 150, 255), 3)
    cv2.ellipse(overlay, (center_x, center_y), (size//2, int(size*0.7)), 0, 0, 360, (100, 200, 255), 2)
    cv2.ellipse(overlay, (center_x, center_y), (size//2-5, int(size*0.7)-5), 0, 0, 360, (120, 220, 255), 1)
    cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)
    return frame

def analyze_face_quality(face_region):
    """Analyze face quality and return feedback"""
    h, w = face_region.shape[:2]
    gray = cv2.cvtColor(face_region, cv2.COLOR_BGR2GRAY)
    
    feedback = []
    score = 100
    
    # Check size
    if w < 100 or h < 100:
        feedback.append("Move closer")
        score -= 30
    elif w > 450 or h > 450:
        feedback.append("Move back")
        score -= 20
    else:
        score += 5
    
    # Check brightness with improved algorithm
    brightness = np.mean(gray)
    if brightness < 40:
        feedback.append("Much darker - add light")
        score -= 30
    elif brightness < 60:
        feedback.append("Too dark")
        score -= 20
    elif brightness > 210:
        feedback.append("Too bright")
        score -= 20
    elif brightness > 190:
        feedback.append("Slightly bright")
        score -= 10
    else:
        score += 5
    
    # Check blur with adaptive threshold
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    if laplacian_var < 30:
        feedback.append("Very blurry - hold still")
        score -= 30
    elif laplacian_var < 50:
        feedback.append("Slightly blurry")
        score -= 15
    else:
        score += 5
    
    # Check face symmetry
    face_center_x = w // 2
    left_brightness = np.mean(gray[:, :face_center_x])
    right_brightness = np.mean(gray[:, face_center_x:])
    symmetry_diff = abs(left_brightness - right_brightness)
    
    if symmetry_diff > 30:
        feedback.append("Face lighting uneven")
        score -= 10
    
    score = max(0, min(100, score))
    
    if not feedback:
        feedback.append("Perfect!")
    
    return score, feedback

def draw_quality_bar(frame, score, x, y, w, h):
    """Draw quality score bar with gradient and modern styling"""
    bar_length = 220
    bar_height = 25
    bar_x = x + (w - bar_length) // 2
    bar_y = y + h + 25
    
    # Background with gradient effect
    overlay = frame.copy()
    cv2.rectangle(overlay, (bar_x-5, bar_y-5), (bar_x + bar_length+5, bar_y + bar_height+5), (30, 30, 30), -1)
    cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
    
    cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_length, bar_y + bar_height), (40, 40, 40), -1)
    
    fill_length = int(bar_length * (score / 100))
    if score >= 80:
        color = (0, 255, 100)  # Bright green
    elif score >= 50:
        color = (0, 200, 255)  # Orange
    else:
        color = (0, 100, 255)  # Red
    
    # Gradient fill
    if fill_length > 0:
        overlay = frame.copy()
        cv2.rectangle(overlay, (bar_x, bar_y), (bar_x + fill_length, bar_y + bar_height), color, -1)
        cv2.addWeighted(overlay, 0.8, frame, 0.2, 0, frame)
    
    # Border with highlight
    cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_length, bar_y + bar_height), (200, 200, 200), 2)
    cv2.rectangle(frame, (bar_x-1, bar_y-1), (bar_x + bar_length+1, bar_y + bar_height+1), (100, 100, 100), 1)
    
    # Quality text with shadow
    draw_text_with_shadow(frame, f"QUALITY: {score}%", (bar_x, bar_y - 10), 
                         cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1)

try:
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("❌ ERROR: Could not open webcam!")
        sys.exit(1)
    
    # Set camera properties
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    cap.set(cv2.CAP_PROP_FPS, 30)
    
    print("✅ Webcam opened successfully")
    print("\n" + "="*60)
    print("INSTRUCTIONS:")
    print("="*60)
    print("  🎯 Position your face in the center guide")
    print("  📊 Wait for quality score to reach 80%+")
    print("  ⚡ Auto-capture when positioned correctly")
    print("  🔴 Press ESC to exit")
    print("\n⚠️  Make sure Flask server is running on http://127.0.0.1:5000")
    print("="*60 + "\n")
    
    frame_count = 0
    countdown = -1
    best_frame = None
    best_score = 0
    ready_frames = 0  # Count frames where face is ready
    auto_capture_threshold = 30  # Auto-capture after 30 frames (~1 second) of good quality
    
    while True:
        ret, frame = cap.read()
        
        if not ret:
            print("❌ ERROR: Failed to read from webcam")
            break
        
        frame_count += 1
        h, w = frame.shape[:2]
        center_x, center_y = w // 2, h // 2
        
        # Create modern gradient overlay
        overlay = frame.copy()
        # Top gradient
        for i in range(140):
            alpha = 0.6 * (1 - i/140)
            cv2.line(overlay, (0, i), (w, i), (10, 20, 40), 2)
        # Bottom gradient  
        for i in range(100):
            alpha = 0.6 * (i/100)
            cv2.line(overlay, (0, h-100+i), (w, h-100+i), (10, 20, 40), 2)
        cv2.addWeighted(overlay, 0.5, frame, 0.5, 0, frame)
        
        # Detect faces using improved method
        if use_dnn:
            faces_raw = detect_faces_dnn(frame, conf_threshold=0.6)
        else:
            faces_raw = detect_faces_haar(frame)
        
        # Apply smoothing
        faces = tracker.update(faces_raw)
        
        # Modern header with shadow
        draw_text_with_shadow(frame, "FACE ATTENDANCE SYSTEM", (25, 45), 
                             cv2.FONT_HERSHEY_DUPLEX, 1.3, (100, 200, 255), 2, 3)
        
        # Instruction bar
        cv2.rectangle(frame, (15, 65), (w-15, 95), (40, 40, 60), -1)
        cv2.rectangle(frame, (15, 65), (w-15, 95), (100, 150, 255), 2)
        draw_text_with_shadow(frame, "Auto-Capture Enabled  |  [ESC] Exit", (30, 85), 
                             cv2.FONT_HERSHEY_SIMPLEX, 0.6, (220, 220, 220), 1, 2)
        
        # Modern timestamp with icon
        timestamp = datetime.now().strftime("%Y-%m-%d  %H:%M:%S")
        draw_text_with_shadow(frame, f"  {timestamp}", (25, h - 25), 
                             cv2.FONT_HERSHEY_SIMPLEX, 0.65, (180, 220, 255), 1, 2)
        
        # Status indicator
        if len(faces) == 0:
            status_text = "NO FACE DETECTED"
            status_color = (0, 120, 255)
            draw_face_guide(frame, center_x, center_y, 220)
            
            # Animated pulsing message
            pulse = int(30 * abs(np.sin(frame_count * 0.1)))
            draw_text_with_shadow(frame, "Position Your Face", (center_x - 150, center_y + 140), 
                                 cv2.FONT_HERSHEY_DUPLEX, 0.9, (100 + pulse, 180 + pulse, 255), 2, 3)
            draw_text_with_shadow(frame, "in the guide", (center_x - 90, center_y + 170), 
                                 cv2.FONT_HERSHEY_SIMPLEX, 0.7, (180, 200, 255), 1, 2)
        elif len(faces) > 1:
            status_text = "MULTIPLE FACES DETECTED"
            status_color = (0, 200, 255)
            # Draw warning boxes for each face
            for face_data in faces:
                fx, fy, fw, fh = face_data[:4]
                # Animated warning boxes
                pulse_w = int(5 * abs(np.sin(frame_count * 0.15)))
                cv2.rectangle(frame, (fx-pulse_w, fy-pulse_w), (fx+fw+pulse_w, fy+fh+pulse_w), (0, 200, 255), 3)
            # Warning message
            draw_text_with_shadow(frame, "Please ensure only ONE person", (center_x - 220, center_y), 
                                 cv2.FONT_HERSHEY_DUPLEX, 0.9, (0, 220, 255), 2, 3)
        else:
            # Single face detected
            face_data = faces[0]
            x, y, w, h = face_data[:4]
            confidence = face_data[4] if len(face_data) > 4 else 0.8
            
            face_region = frame[y:y+h, x:x+w]
            
            # Analyze quality
            score, feedback = analyze_face_quality(face_region)
            
            # Save best frame
            if score > best_score:
                best_score = score
                best_frame = frame.copy()
            
            # Draw face rectangle with quality-based color
            if score >= 80:
                rect_color = (0, 255, 0)
                status_text = "READY TO CAPTURE"
                status_color = (0, 255, 0)
            elif score >= 50:
                rect_color = (0, 200, 255)
                status_text = "GOOD - Improve for better results"
                status_color = (0, 200, 255)
            else:
                rect_color = (0, 0, 255)
                status_text = "POOR QUALITY"
                status_color = (0, 0, 255)
            
            # Draw modern face tracking corners with glow
            thickness = 4
            corner_length = 35
            
            # Detection confidence badge
            badge_x, badge_y = x, y - 60
            cv2.rectangle(frame, (badge_x, badge_y), (badge_x + 140, badge_y + 30), (40, 40, 60), -1)
            cv2.rectangle(frame, (badge_x, badge_y), (badge_x + 140, badge_y + 30), rect_color, 2)
            conf_text = f"DETECT: {int(confidence * 100)}%"
            draw_text_with_shadow(frame, conf_text, (badge_x + 10, badge_y + 20), 
                                 cv2.FONT_HERSHEY_DUPLEX, 0.5, (255, 255, 255), 1, 2)
            
            # Glowing corners with outer glow
            glow_color = tuple(int(c * 0.5) for c in rect_color)
            # Outer glow
            cv2.line(frame, (x-2, y-2), (x + corner_length+2, y-2), glow_color, thickness+2)
            cv2.line(frame, (x-2, y-2), (x-2, y + corner_length+2), glow_color, thickness+2)
            cv2.line(frame, (x + w+2, y-2), (x + w - corner_length-2, y-2), glow_color, thickness+2)
            cv2.line(frame, (x + w+2, y-2), (x + w+2, y + corner_length+2), glow_color, thickness+2)
            cv2.line(frame, (x-2, y + h+2), (x + corner_length+2, y + h+2), glow_color, thickness+2)
            cv2.line(frame, (x-2, y + h+2), (x-2, y + h - corner_length-2), glow_color, thickness+2)
            cv2.line(frame, (x + w+2, y + h+2), (x + w - corner_length-2, y + h+2), glow_color, thickness+2)
            cv2.line(frame, (x + w+2, y + h+2), (x + w+2, y + h - corner_length-2), glow_color, thickness+2)
            
            # Main corners
            cv2.line(frame, (x, y), (x + corner_length, y), rect_color, thickness)
            cv2.line(frame, (x, y), (x, y + corner_length), rect_color, thickness)
            cv2.line(frame, (x + w, y), (x + w - corner_length, y), rect_color, thickness)
            cv2.line(frame, (x + w, y), (x + w, y + corner_length), rect_color, thickness)
            cv2.line(frame, (x, y + h), (x + corner_length, y + h), rect_color, thickness)
            cv2.line(frame, (x, y + h), (x, y + h - corner_length), rect_color, thickness)
            cv2.line(frame, (x + w, y + h), (x + w - corner_length, y + h), rect_color, thickness)
            cv2.line(frame, (x + w, y + h), (x + w, y + h - corner_length), rect_color, thickness)
            
            # Draw quality bar
            draw_quality_bar(frame, score, x, y, w, h)
            
            # Draw feedback with styled badges
            feedback_y = y - 95
            for i, text in enumerate(feedback):
                text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_DUPLEX, 0.6, 1)[0]
                badge_w = text_size[0] + 20
                badge_x = x
                badge_y = feedback_y - (i * 30)
                
                # Badge background
                cv2.rectangle(frame, (badge_x, badge_y - 20), (badge_x + badge_w, badge_y + 5), (30, 30, 50), -1)
                cv2.rectangle(frame, (badge_x, badge_y - 20), (badge_x + badge_w, badge_y + 5), (255, 200, 100), 2)
                
                # Text with shadow
                draw_text_with_shadow(frame, text, (badge_x + 10, badge_y), 
                                     cv2.FONT_HERSHEY_DUPLEX, 0.55, (255, 255, 100), 1, 2)
            
            # Center alignment indicator with animated arrows
            face_center_x = x + w // 2
            face_center_y = y + h // 2
            offset_x = abs(face_center_x - center_x)
            
            # Auto-capture logic
            if score >= 80 and offset_x <= 50 and countdown <= 0:
                ready_frames += 1
                # Show progress indicator
                progress_width = int(200 * (ready_frames / auto_capture_threshold))
                cv2.rectangle(frame, (center_x - 100, 120), (center_x + 100, 140), (40, 40, 60), -1)
                cv2.rectangle(frame, (center_x - 100, 120), (center_x - 100 + progress_width, 140), (0, 255, 100), -1)
                cv2.rectangle(frame, (center_x - 100, 120), (center_x + 100, 140), (100, 255, 150), 2)
                draw_text_with_shadow(frame, "AUTO-CAPTURING...", (center_x - 90, 110), 
                                    cv2.FONT_HERSHEY_DUPLEX, 0.6, (100, 255, 150), 1, 2)
                
                if ready_frames >= auto_capture_threshold:
                    countdown = 3
                    ready_frames = 0
            else:
                ready_frames = 0  # Reset if conditions not met
            
            if offset_x > 50:
                arrow_pulse = int(10 * abs(np.sin(frame_count * 0.2)))
                if face_center_x < center_x:
                    # Right arrow with animation
                    arrow_x = 40 + arrow_pulse
                    cv2.arrowedLine(frame, (arrow_x, center_y), (arrow_x + 60, center_y), (0, 255, 255), 5, tipLength=0.4)
                    draw_text_with_shadow(frame, "MOVE RIGHT", (arrow_x + 70, center_y + 10), 
                                        cv2.FONT_HERSHEY_DUPLEX, 0.8, (0, 255, 255), 2, 3)
                else:
                    # Left arrow with animation
                    arrow_x = w - 110 - arrow_pulse
                    cv2.arrowedLine(frame, (arrow_x + 60, center_y), (arrow_x, center_y), (0, 255, 255), 5, tipLength=0.4)
                    draw_text_with_shadow(frame, "MOVE LEFT", (arrow_x - 160, center_y + 10), 
                                        cv2.FONT_HERSHEY_DUPLEX, 0.8, (0, 255, 255), 2, 3)
        
        # Modern footer status bar
        status_bar_y = h - 65
        # Status badge
        cv2.rectangle(frame, (15, status_bar_y), (w//2 - 10, status_bar_y + 35), (30, 30, 50), -1)
        cv2.rectangle(frame, (15, status_bar_y), (w//2 - 10, status_bar_y + 35), status_color, 3)
        draw_text_with_shadow(frame, f"STATUS: {status_text}", (25, status_bar_y + 23), 
                             cv2.FONT_HERSHEY_DUPLEX, 0.65, status_color, 1, 2)
        
        # Best score badge
        cv2.rectangle(frame, (w//2 + 10, status_bar_y), (w - 15, status_bar_y + 35), (30, 30, 50), -1)
        score_color = (0, 255, 100) if best_score >= 80 else (0, 200, 255) if best_score >= 50 else (100, 100, 255)
        cv2.rectangle(frame, (w//2 + 10, status_bar_y), (w - 15, status_bar_y + 35), score_color, 3)
        draw_text_with_shadow(frame, f"BEST SCORE: {best_score}%", (w//2 + 20, status_bar_y + 23), 
                             cv2.FONT_HERSHEY_DUPLEX, 0.65, score_color, 1, 2)
        
        # Modern countdown with circular progress
        if countdown > 0:
            countdown_overlay = frame.copy()
            cv2.rectangle(countdown_overlay, (0, 0), (w, h), (0, 0, 0), -1)
            cv2.addWeighted(countdown_overlay, 0.6, frame, 0.4, 0, frame)
            
            # Circular progress
            radius = 120
            angle = int(360 * (3 - countdown) / 3)
            cv2.ellipse(frame, (center_x, center_y), (radius, radius), -90, 0, angle, (0, 255, 150), 15)
            cv2.circle(frame, (center_x, center_y), radius + 20, (50, 100, 200), 3)
            
            # Countdown number with glow
            for offset in [(4, 4), (2, 2), (0, 0)]:
                alpha = 0.3 if offset[0] > 0 else 1.0
                color = (0, int(200 * alpha), int(255 * alpha))
                cv2.putText(frame, str(countdown), (center_x - 60 + offset[0], center_y + 80 + offset[1]), 
                           cv2.FONT_HERSHEY_DUPLEX, 6, color, 8 if offset[0] > 0 else 6)
            
            # Countdown text
            draw_text_with_shadow(frame, "GET READY...", (center_x - 120, center_y - 100), 
                                 cv2.FONT_HERSHEY_DUPLEX, 1.2, (100, 255, 255), 2, 3)
        
        cv2.imshow('Face Attendance', frame)
        
        key = cv2.waitKey(1) & 0xFF
        
        if countdown > 0:
            countdown -= 1
            if countdown == 0:
                # Capture best frame
                if best_frame is not None:
                    frame_to_send = best_frame
                else:
                    frame_to_send = frame
                
                _, buffer = cv2.imencode('.jpg', frame_to_send)
                img_base64 = base64.b64encode(buffer).decode('utf-8')
                
                print(f"\n📸 Capturing face... (Quality: {best_score}%)")
                print("📤 Sending to server...")
                
                try:
                    response = requests.post(
                        'http://127.0.0.1:5000/api/mark-attendance',
                        json={'image': img_base64},
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        print("\n✅ SUCCESS!")
                        print(f"   Employee: {data.get('employee_name', 'Unknown')}")
                        
                        # Handle both new attendance and already marked cases
                        if 'marked_at' in data:
                            print(f"   Note: {data.get('message', 'Already marked')}")
                            print(f"   Time: {data.get('marked_at', 'N/A')}")
                        else:
                            print(f"   Time: {data.get('timestamp', 'N/A')}")
                            print(f"   Confidence: {data.get('confidence', 0):.1%}")
                        
                        print("\n👋 Attendance recorded! Exiting in 2 seconds...")
                        cv2.waitKey(2000)  # Wait 2 seconds to show success
                        break  # Exit the loop
                    else:
                        error_data = response.json()
                        print(f"\n❌ ERROR: {error_data.get('error', 'Unknown error')}")
                        if 'issues' in error_data:
                            print(f"   Issues: {', '.join(error_data['issues'])}")
                        print("   Resetting for retry...")
                except requests.exceptions.ConnectionError:
                    print("\n❌ ERROR: Cannot connect to server")
                    print("   Make sure Flask server is running: python app.py")
                    print("   Resetting for retry...")
                except Exception as e:
                    print(f"\n❌ ERROR: {e}")
                    print("   Resetting for retry...")
                
                # Reset for next capture
                best_score = 0
                best_frame = None
                countdown = -1
        
        elif key == 27:  # ESC
            print("\n👋 Exiting...")
            break

except KeyboardInterrupt:
    print("\n\n👋 Interrupted by user")
except Exception as e:
    print(f"\n❌ ERROR: {e}")
finally:
    cap.release()
    cv2.destroyAllWindows()
    print("✅ Cleanup complete")
