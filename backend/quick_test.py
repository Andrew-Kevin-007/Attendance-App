import cv2
import base64
import requests
import numpy as np

# Initialize face cascade
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')  # type: ignore

def analyze_face_quality(face_region):
    """Analyze face quality and return feedback"""
    h, w = face_region.shape[:2]
    gray = cv2.cvtColor(face_region, cv2.COLOR_BGR2GRAY)
    
    feedback = []
    score = 100
    
    if w < 120 or h < 120:
        feedback.append("Move closer")
        score -= 30
    elif w > 400 or h > 400:
        feedback.append("Move back")
        score -= 20
    
    brightness = np.mean(gray)
    if brightness < 50:
        feedback.append("More light needed")
        score -= 25
    elif brightness > 220:
        feedback.append("Too bright")
        score -= 20
    
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    if laplacian_var < 50:
        feedback.append("Hold steady")
        score -= 25
    
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
        color = (0, 255, 100)
    elif score >= 50:
        color = (0, 200, 255)
    else:
        color = (0, 100, 255)
    
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

print("="*60)
print("   PROFESSIONAL EMPLOYEE REGISTRATION")
print("="*60)
print("\n📸 Opening webcam for face registration...")
print("\nINSTRUCTIONS:")
print("  🎯 Position your face in the center")
print("  📊 Wait for quality score 80%+")
print("  🔵 Press SPACE to capture")
print("  🔴 Press ESC to exit")
print("="*60 + "\n")

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

best_frame = None
best_score = 0
countdown = -1

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    h, w = frame.shape[:2]
    center_x, center_y = w // 2, h // 2
    
    # Header overlay
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (w, 100), (0, 0, 0), -1)
    cv2.rectangle(overlay, (0, h-60), (w, h), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.4, frame, 0.6, 0, frame)
    
    # Detect faces
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(100, 100))
    
    # Modern header
    draw_text_with_shadow(display_frame, "EMPLOYEE REGISTRATION", (25, 45), 
                         cv2.FONT_HERSHEY_DUPLEX, 1.3, (100, 255, 200), 2, 3)
    
    # Instruction bar
    cv2.rectangle(display_frame, (15, 65), (w-15, 95), (40, 40, 60), -1)
    cv2.rectangle(display_frame, (15, 65), (w-15, 95), (100, 255, 200), 2)
    draw_text_with_shadow(display_frame, "[SPACE] Capture  |  [ESC] Exit", (30, 85), 
        status_color = (0, 120, 255)
        # Animated guide
        overlay = display_frame.copy()
        cv2.ellipse(overlay, (center_x, center_y), (120, 160), 0, 0, 360, (100, 180, 255), 3)
        cv2.ellipse(overlay, (center_x, center_y), (115, 155), 0, 0, 360, (120, 200, 255), 2)
        cv2.addWeighted(overlay, 0.7, display_frame, 0.3, 0, display_frame)
        draw_text_with_shadow(display_frame, "Position Your Face", (center_x - 140, center_y + 120), 
                             cv2.FONT_HERSHEY_DUPLEX, 0.8, (150, 200, 255), 2, 3)
    if len(faces) == 0:
        status_text = "NO FACE DETECTED"
        status_color = (0, 0, 255)
        cv2.ellipse(frame, (center_x, center_y), (110, 150), 0, 0, 360, (255, 255, 255), 2)
    elif len(faces) > 1:
        status_text = "MULTIPLE FACES DETECTED"
        status_color = (0, 165, 255)
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 165, 255), 2)
    else:
        x, y, w, h = faces[0]
        face_region = frame[y:y+h, x:x+w]
        score, feedback = analyze_face_quality(face_region)
        
        if score > best_score:
            best_score = score
            best_frame = frame.copy()
        
        rect_color = (0, 255, 0) if score >= 80 else (0, 200, 255) if score >= 50 else (0, 0, 255)
        status_text = "READY" if score >= 80 else "IMPROVING..." if score >= 50 else "POOR QUALITY"
        status_color = rect_color
        
        # Draw tracking corners
        thickness = 3
        corner_length = 30
        cv2.line(frame, (x, y), (x + corner_length, y), rect_color, thickness)
        cv2.line(frame, (x, y), (x, y + corner_length), rect_color, thickness)
        cv2.line(frame, (x + w, y), (x + w - corner_length, y), rect_color, thickness)
        cv2.line(frame, (x + w, y), (x + w, y + corner_length), rect_color, thickness)
        cv2.line(frame, (x, y + h), (x + corner_length, y + h), rect_color, thickness)
        cv2.line(frame, (x, y + h), (x, y + h - corner_length), rect_color, thickness)
        cv2.line(frame, (x + w, y + h), (x + w - corner_length, y + h), rect_color, thickness)
        cv2.line(frame, (x + w, y + h), (x + w, y + h - corner_length), rect_color, thickness)
        
        draw_quality_bar(frame, score, x, y, w, h)
        
        for i, text in enumerate(feedback):
            cv2.putText(frame, text, (x, y - 20 - (i * 25)), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    
    # Status bar
    cv2.rectangle(frame, (0, h-60), (w, h-30), (50, 50, 50), -1)
    cv2.putText(frame, status_text, (w//2 - len(status_text)*6, h - 40), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)
    
    # Countdown
    if countdown > 0:
        countdown_overlay = frame.copy()
        cv2.rectangle(countdown_overlay, (0, 0), (w, h), (0, 0, 0), -1)
        cv2.addWeighted(countdown_overlay, 0.5, frame, 0.5, 0, frame)
        cv2.putText(frame, str(countdown), (center_x - 50, center_y), 
                   cv2.FONT_HERSHEY_DUPLEX, 5, (0, 255, 0), 8)
        countdown -= 1
    elif countdown == 0:
        capture_frame = best_frame if best_frame is not None else frame
        _, buffer = cv2.imencode('.jpg', capture_frame)
        img_b64 = base64.b64encode(buffer).decode('utf-8')
        
        cap.release()
        cv2.destroyAllWindows()
        
        print("\n✅ Face captured!")
        print(f"📊 Quality Score: {best_score}%")
        name = input("\nEnter employee name: ").strip()
        email = input("Enter employee email: ").strip()
        
        if name and email:
            data = {
                "name": name,
                "email": email,
                "image": f"data:image/jpeg;base64,{img_b64}"
            }
            
            try:
                response = requests.post("http://127.0.0.1:5000/api/register-face", json=data)
                result = response.json()
                
                if response.status_code == 201:
                    print("\n" + "✅ "*20)
                    print("  REGISTRATION SUCCESSFUL!")
                    print("✅ "*20)
                    print(f"\n   Employee ID: {result.get('employee_id')}")
                    print(f"   Name: {result.get('name')}")
                    print(f"   Email: {result.get('email')}")
                    print(f"   Quality: {best_score}%")
                    print("\n" + "="*60)
                else:
                    print(f"\n❌ Registration failed: {result.get('error')}")
            except Exception as e:
                print(f"\n❌ Error: {e}")
        break
    
    cv2.imshow('Professional Employee Registration', frame)
    
    key = cv2.waitKey(1)
    if key == 32 and countdown == -1:
        if len(faces) == 1:
            countdown = 3
        else:
            print("\n⚠️  Ensure only ONE face is visible\n")
    elif key == 27:
        break

cap.release()
cv2.destroyAllWindows()