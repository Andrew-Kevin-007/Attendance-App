# Attendance Tracker

Enterprise task management with facial recognition attendance.

## 📁 Project Structure

```text
attendance-tracker/
├── backend/          # FastAPI + Flask backend
│   ├── app/         # FastAPI application
│   ├── flask_app.py # Face recognition service
│   └── *.py         # Face utils, models, config
└── frontend/        # React + TypeScript
    └── src/         # Application code
```

## 🚀 Quick Start

### Backend

```bash
cd backend

# Setup virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Configure
copy .env.example .env
# Edit .env - set SECRET_KEY (use: openssl rand -hex 32)

# Run server
python -m uvicorn app.main:app --host 127.0.0.1 --port 8001
```

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Configure
copy .env.example .env

# Run development server
npm run dev
```

## 🌐 Access

- **Frontend**: [http://localhost:5173](http://localhost:5173)
- **Backend API**: [http://127.0.0.1:8001](http://127.0.0.1:8001)
- **API Docs**: [http://127.0.0.1:8001/api/docs](http://127.0.0.1:8001/api/docs)

## ✨ Features

- **Task Management**: Create, assign, track tasks
- **Face Attendance**: Facial recognition for attendance marking
- **Role-Based Access**: Admin, Manager, Employee roles
- **Real-Time Notifications**: Instant updates
- **Analytics Dashboard**: Performance metrics
- **Secure Authentication**: JWT-based auth

## 🔑 Default Roles

- **Admin**: Full system access, user management, attendance reports
- **Manager**: Task creation, team oversight, face enrollment
- **Employee**: Personal tasks, mark own attendance

## 📚 Documentation

- **Backend**: See `backend/README.md`
- **API Docs**: Available at `/api/docs` when server running
- **Production**: See `PRODUCTION.md` for deployment guide

## 🛠️ Tech Stack

**Backend**:

- FastAPI (REST API)
- Flask (Face service)
- SQLAlchemy (ORM)
- OpenCV (Face recognition)
- JWT Authentication

**Frontend**:

- React 18
- TypeScript
- TailwindCSS
- Vite
- Shadcn/ui

## 🔒 Security

- JWT token authentication
- Role-based authorization
- Face data encryption
- CORS protection
- Input validation
- HTTPS required in production

## 📝 License

MIT License - See LICENSE file

---

**Version**: 1.0.0  
**Last Updated**: December 2025
