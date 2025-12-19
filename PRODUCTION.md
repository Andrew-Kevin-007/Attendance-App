# Production Deployment Guide

## 🚀 Pre-Deployment Checklist

### Environment Variables

#### Backend (`backend/.env`)
```bash
DATABASE_URL=postgresql://user:pass@host:5432/dbname  # Use PostgreSQL in production
SECRET_KEY=<generate-with-openssl-rand-hex-32>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
HOST=0.0.0.0
PORT=8001
```

#### Frontend
Update `src/lib/api.ts` and `src/lib/attendance.ts`:
```typescript
const API_BASE_URL = import.meta.env.VITE_API_URL || "https://api.yourdomain.com";
```

### Security Hardening

1. **Generate secure SECRET_KEY:**
   ```bash
   openssl rand -hex 32
   ```

2. **Update CORS origins** to production domains only

3. **Enable HTTPS** for all endpoints

4. **Database:**
   - Migrate from SQLite to PostgreSQL/MySQL
   - Enable backups
   - Use connection pooling

5. **Rate Limiting:**
   Add rate limiting middleware to FastAPI routes

6. **Input Validation:**
   All endpoints already use Pydantic models for validation ✓

### Build Frontend

```bash
cd frontend
npm install
npm run build
```

Output will be in `frontend/dist/` - serve with nginx or similar.

### Backend Production Server

Replace Uvicorn with Gunicorn + Uvicorn workers:

```bash
pip install gunicorn
cd task-manager
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8001
```

### Nginx Configuration

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    
    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    # Frontend
    location / {
        root /path/to/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Attendance endpoints
    location /attendance {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Face service
    location /face {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Docker Deployment (Optional)

#### Dockerfile (Backend)
```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY task-manager/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY task-manager/ ./task-manager/
COPY face/ ./face/

WORKDIR /app/task-manager

CMD ["gunicorn", "app.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8001"]
```

#### Dockerfile (Frontend)
```dockerfile
FROM node:18-alpine as build

WORKDIR /app
COPY frontend/package*.json ./
RUN npm ci

COPY frontend/ .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
```

#### docker-compose.yml
```yaml
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: attendance
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    environment:
      DATABASE_URL: postgresql://user:password@db:5432/attendance
      SECRET_KEY: ${SECRET_KEY}
      ALLOWED_ORIGINS: https://yourdomain.com
    depends_on:
      - db
    ports:
      - "8001:8001"

  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - backend

volumes:
  postgres_data:
```

## 🔍 Health Checks

- Backend: `GET /`
- Face service: `GET /face/api/health`
- Attendance: `GET /attendance/status-today` (requires auth)

## 📊 Monitoring

Set up:
1. Application logs → CloudWatch/Datadog
2. Error tracking → Sentry
3. Uptime monitoring → UptimeRobot/Pingdom
4. Performance → New Relic/AppDynamics

## 🔐 Backup Strategy

1. **Database:** Automated daily backups
2. **Face encodings:** Backup `face_attendance.db` separately
3. **Uploads:** Sync to S3/cloud storage

## 🚨 Important Notes

- **Camera permissions** must be granted over HTTPS
- **Face data** is sensitive - ensure GDPR/privacy compliance
- **Rate limit** face recognition endpoints to prevent abuse
- **Monitor** upload directory size (face images accumulate)
- **Test** face recognition with various lighting conditions before launch

## 📈 Scaling Considerations

- **Face recognition** is CPU-intensive - consider GPU instances
- **Database** connection pooling for concurrent users
- **Load balancer** for multiple backend instances
- **CDN** for static frontend assets
- **Redis** for session management and caching
