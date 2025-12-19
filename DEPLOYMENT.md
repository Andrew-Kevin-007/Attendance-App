# Attendance Tracker Deployment Guide

## Quick Local Development

### Option 1: Manual Start (Recommended)

**Terminal 1 - Backend:**
```powershell
cd backend
D:\Attendancetracker\.venv312\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8001
```

**Terminal 2 - Frontend:**
```powershell
cd frontend
npm run dev
```

### Option 2: Using Start Scripts (Windows)

```powershell
# From project root - requires execution policy bypass
powershell -ExecutionPolicy Bypass -File .\start-all.ps1
```

---

## Production Deployment

### Frontend Build

```powershell
cd frontend
npm run build:prod
```

This creates a `dist/` folder with static files. Serve with any static hosting (Nginx, Vercel, Netlify, etc.).

### Backend Deployment

**Option A: Docker (Recommended)**

Create `backend/Dockerfile`:
```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create uploads directory
RUN mkdir -p uploads/registrations uploads/attendance

EXPOSE 8001
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
```

Build and run:
```bash
cd backend
docker build -t attendance-backend .
docker run -d -p 8001:8001 --env-file .env attendance-backend
```

**Option B: Systemd Service (Linux)**

Create `/etc/systemd/system/attendance-backend.service`:
```ini
[Unit]
Description=Attendance Tracker Backend
After=network.target

[Service]
User=www-data
WorkingDirectory=/opt/attendance-tracker/backend
Environment="PATH=/opt/attendance-tracker/.venv/bin"
ExecStart=/opt/attendance-tracker/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8001
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable attendance-backend
sudo systemctl start attendance-backend
```

**Option C: Windows Service**

Use NSSM (Non-Sucking Service Manager):
```powershell
# Install NSSM
choco install nssm

# Create service
nssm install AttendanceBackend "D:\Attendancetracker\.venv312\Scripts\python.exe"
nssm set AttendanceBackend AppParameters "-m uvicorn app.main:app --host 0.0.0.0 --port 8001"
nssm set AttendanceBackend AppDirectory "D:\Attendancetracker\backend"
nssm start AttendanceBackend
```

---

## Environment Configuration

### Backend (.env)

```bash
# Security - REQUIRED: Generate with `openssl rand -hex 32`
SECRET_KEY=your_secret_key_here

# JWT Settings
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Server
HOST=0.0.0.0
PORT=8001

# CORS - Update for production domains
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Database (optional - defaults to SQLite)
# DATABASE_URL=postgresql://user:pass@host:5432/attendance_tracker
```

### Frontend (.env.production)

```bash
VITE_API_URL=https://api.yourdomain.com
```

---

## Nginx Reverse Proxy (Production)

```nginx
# /etc/nginx/sites-available/attendance-tracker

# Frontend
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    
    root /var/www/attendance-tracker/frontend/dist;
    index index.html;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    # API proxy
    location /api {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Face service proxy
    location /face {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    # Auth proxy
    location /auth {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    # Tasks proxy
    location /tasks {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    # Attendance proxy
    location /attendance {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        client_max_body_size 10M;  # For face image uploads
    }
    
    # Notifications proxy
    location /notifications {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Enable site and get SSL:
```bash
sudo ln -s /etc/nginx/sites-available/attendance-tracker /etc/nginx/sites-enabled/
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
sudo systemctl reload nginx
```

---

## Database Migration (SQLite to PostgreSQL)

For production, switch to PostgreSQL:

1. Install PostgreSQL and create database:
```bash
sudo -u postgres createdb attendance_tracker
sudo -u postgres createuser attendance_user -P
sudo -u postgres psql -c "GRANT ALL ON DATABASE attendance_tracker TO attendance_user;"
```

2. Update backend `.env`:
```bash
DATABASE_URL=postgresql://attendance_user:password@localhost/attendance_tracker
```

3. Install driver:
```bash
pip install psycopg2-binary
```

4. Tables auto-create on first run.

---

## Health Checks

- Backend: `GET http://127.0.0.1:8001/health`
- API docs: `GET http://127.0.0.1:8001/api/docs`
- Face service: `GET http://127.0.0.1:8001/face/api/health`

---

## Troubleshooting

### Port Already in Use
```powershell
# Find and kill process on port 8001
netstat -ano | findstr :8001
taskkill /PID <PID> /F
```

### OpenCV Issues
Don't use `--reload` flag with uvicorn (subprocess import issues).

### CORS Errors
Update `ALLOWED_ORIGINS` in backend `.env` to include your frontend domain.

### Face Recognition Not Working
- Ensure `uploads/` directory exists with proper permissions
- Check camera permissions in browser
- Verify face is properly lit and centered
