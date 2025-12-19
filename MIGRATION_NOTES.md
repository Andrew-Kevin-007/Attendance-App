# Migration to Two-Directory Structure

## Overview

The project has been reorganized from a scattered structure into a clean two-directory layout:

**Before:**
```
project-root/
├── task-manager/          # FastAPI backend
│   └── app/
├── face/backend/          # Flask face service
└── frontend/              # React app
```

**After:**
```
project-root/
├── backend/               # All backend code (FastAPI + Flask)
│   ├── app/              # FastAPI application
│   ├── flask_app.py      # Flask face service
│   └── *.py              # Face utilities
└── frontend/              # React app (unchanged)
```

## Changes Made

### 1. Directory Consolidation

- **Created** `backend/` directory
- **Moved** all Python backend code into `backend/`:
  - `task-manager/app/` → `backend/app/`
  - `face/backend/*.py` → `backend/*.py`
- **Renamed** `backend/app.py` → `backend/flask_app.py` to avoid naming conflict

### 2. Import Path Updates

#### backend/app/routers/attendance.py
- Updated to import face modules from backend root:
  ```python
  backend_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
  sys.path.insert(0, backend_root)
  ```

#### backend/app/attendance_mount.py
- Updated Flask app path to load from `backend/flask_app.py`:
  ```python
  flask_app_path = os.path.join(backend_root, "flask_app.py")
  ```

### 3. Documentation Updates

- Updated `README.md` with new structure
- Updated `SETUP_GUIDE.md` with new paths
- Updated `PRODUCTION.md` to reference `backend/` directory
- Created `backend/README.md` with backend-specific docs

### 4. Configuration Files

- Created `backend/requirements.txt` with all dependencies
- Created `backend/.env.example` with environment template
- No changes needed to frontend configuration

### 5. Startup Scripts

Created convenient startup scripts:
- **`backend/start.ps1`** - Start backend server
- **`frontend/start.ps1`** - Start frontend dev server
- **`start-all.ps1`** - Start both in separate windows (root level)

## Testing the New Structure

### 1. Test Imports

```powershell
cd backend
python test_imports.py
```

Should output: ✅ All imports successful!

### 2. Start Backend

```powershell
cd backend
D:\Attendancetracker\.venv312\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8001
```

Or use the startup script:
```powershell
cd backend
.\start.ps1
```

### 3. Verify Endpoints

- Health check: http://127.0.0.1:8001/health
- API docs: http://127.0.0.1:8001/api/docs
- Face service: http://127.0.0.1:8001/face/api/health

### 4. Start Frontend

```powershell
cd frontend
npm run dev
```

Or use the startup script:
```powershell
cd frontend
.\start.ps1
```

### 5. Full Stack Test

From project root:
```powershell
.\start-all.ps1
```

## Breaking Changes

### None for End Users

The API URLs remain unchanged:
- Backend still runs on port 8001
- All endpoints maintain same paths
- Frontend configuration unchanged

### For Developers

If you were importing modules directly:
- Old: `from face/backend import face_utils`
- New: `import face_utils` (with backend/ in sys.path)

Database files remain in place:
- `backend/task.db` - Main app database
- `backend/face_attendance.db` - Face recognition database

## Old Directories

The old directories (`task-manager/` and `face/`) can be safely deleted after verifying the new structure works correctly. They are no longer needed.

## Benefits of New Structure

1. **Cleaner organization** - All backend code in one place
2. **Easier deployment** - Single backend directory to deploy
3. **Simpler paths** - No nested directory navigation
4. **Better scalability** - Clear separation of concerns
5. **Standard layout** - Follows industry best practices

## Rollback (if needed)

If you need to rollback:

1. The old directories are still present (just not used)
2. Change working directory back to `task-manager/`
3. Run uvicorn from there with old command

However, the new structure is tested and working, so rollback should not be necessary.

## Next Steps

1. ✅ Verify backend starts correctly
2. ✅ Test all API endpoints
3. ✅ Confirm face recognition works
4. ⏳ Remove old directories (`task-manager/`, `face/`) after testing
5. ⏳ Update any deployment scripts or CI/CD pipelines
6. ⏳ Inform team members of new structure

## Support

If you encounter any issues with the new structure:

1. Check `backend/test_imports.py` output
2. Verify `.env` file exists in `backend/`
3. Ensure virtual environment is activated
4. Confirm OpenCV installed: `pip list | findstr opencv`
5. Review `backend/README.md` for troubleshooting

## File Mapping Reference

| Old Location | New Location |
|--------------|--------------|
| `task-manager/app/main.py` | `backend/app/main.py` |
| `task-manager/app/routers/` | `backend/app/routers/` |
| `face/backend/app.py` | `backend/flask_app.py` |
| `face/backend/face_utils.py` | `backend/face_utils.py` |
| `face/backend/database.py` | `backend/database.py` |
| `face/backend/models.py` | `backend/models.py` |
| `.venv312/` | `.venv312/` (unchanged) |
| `frontend/` | `frontend/` (unchanged) |
