# Post-Restructure Checklist

Use this checklist to verify the restructure is complete and working.

## Phase 1: Initial Verification

### File Structure
- [ ] `backend/` directory exists
- [ ] `backend/app/` contains FastAPI code
- [ ] `backend/flask_app.py` exists (renamed from app.py)
- [ ] `backend/face_utils.py`, `database.py`, `models.py` exist
- [ ] `backend/requirements.txt` exists
- [ ] `backend/.env.example` exists
- [ ] `backend/start.ps1` exists
- [ ] `frontend/` directory unchanged
- [ ] `frontend/start.ps1` exists
- [ ] `start-all.ps1` exists in root

## Phase 2: Backend Testing

### Import Verification
```powershell
cd backend
D:\Attendancetracker\.venv312\Scripts\python.exe test_imports.py
```
- [ ] All imports successful (no errors)
- [ ] face_utils, database, models imported
- [ ] flask_app imported
- [ ] app.main imported
- [ ] app.routers.attendance imported

### Server Startup
```powershell
cd backend
D:\Attendancetracker\.venv312\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8001
```
- [ ] Server starts without errors
- [ ] No module import errors
- [ ] Face service mounts successfully
- [ ] Database tables created

### Endpoint Verification
Visit these URLs in browser while server running:
- [ ] http://127.0.0.1:8001/ returns JSON status
- [ ] http://127.0.0.1:8001/health returns healthy status
- [ ] http://127.0.0.1:8001/api/docs shows Swagger documentation
- [ ] http://127.0.0.1:8001/face/api/health returns face service status

## Phase 3: Frontend Testing

### Development Server
```powershell
cd frontend
npm run dev
```
- [ ] Server starts on http://localhost:5173
- [ ] No build errors
- [ ] Assets load correctly

### UI Verification
- [ ] Login page loads
- [ ] Can create test account
- [ ] Can login with credentials
- [ ] Redirected to attendance page
- [ ] Webcam UI displays correctly

## Phase 4: Feature Testing

### Authentication
- [ ] Signup works
- [ ] Login works
- [ ] JWT token stored
- [ ] Protected routes work

### Attendance System
- [ ] Attendance page loads webcam
- [ ] Face detection overlay appears
- [ ] Can mark attendance (if face registered)
- [ ] Success/error messages display
- [ ] Dashboard shows attendance status

### Admin/Manager Features
- [ ] Admin can access Register Face page
- [ ] User dropdown loads all users
- [ ] Can capture and register face
- [ ] Today's attendance card shows on dashboard
- [ ] Attendance summary loads correctly

### Task Management
- [ ] Can create tasks
- [ ] Can view tasks list
- [ ] Can update task status
- [ ] Notifications appear

## Phase 5: Startup Scripts

### Backend Script
```powershell
cd backend
.\start.ps1
```
- [ ] Script runs without errors
- [ ] Creates .env from example if missing
- [ ] Creates upload directories if missing
- [ ] Starts uvicorn server
- [ ] Server accessible on port 8001

### Frontend Script
```powershell
cd frontend
.\start.ps1
```
- [ ] Script runs without errors
- [ ] Installs dependencies if needed
- [ ] Creates .env from example if missing
- [ ] Starts Vite dev server
- [ ] Server accessible on port 5173

### All-In-One Script
```powershell
.\start-all.ps1
```
- [ ] Opens two terminal windows
- [ ] Backend window starts successfully
- [ ] Frontend window starts successfully
- [ ] Both remain running

## Phase 6: Cleanup (Optional)

### Remove Old Directories
Only after all above checks pass:
```powershell
# Backup first (optional)
# Rename-Item task-manager task-manager.old
# Rename-Item face face.old

# Or delete directly
# Remove-Item -Recurse task-manager
# Remove-Item -Recurse face
```
- [ ] Backed up or confirmed not needed
- [ ] Deleted old directories (optional)
- [ ] Verified app still works after deletion

## Phase 7: Documentation Review

### Updated Files
- [ ] README.md reflects new structure
- [ ] SETUP_GUIDE.md has correct paths
- [ ] PRODUCTION.md updated for backend/
- [ ] backend/README.md exists and is accurate
- [ ] MIGRATION_NOTES.md explains changes
- [ ] RESTRUCTURE_COMPLETE.md reviewed

## Phase 8: Team Handoff

### Communication
- [ ] Notified team of structure change
- [ ] Shared MIGRATION_NOTES.md
- [ ] Updated deployment documentation
- [ ] Updated CI/CD pipelines (if any)
- [ ] Confirmed no hardcoded old paths

## Final Verification

### Complete Test Flow
1. [ ] Start both servers using `start-all.ps1`
2. [ ] Create new user account
3. [ ] Login with new account
4. [ ] Mark attendance via face (or skip if not registered)
5. [ ] Create a task
6. [ ] Logout and login again
7. [ ] Check dashboard analytics
8. [ ] Test as admin (register face for user)
9. [ ] View today's attendance summary
10. [ ] All features work as expected

## Success Criteria

All checkboxes above should be checked (✓) for successful restructure completion.

## Rollback Plan

If critical issues found:
1. Stop both servers
2. Restore old directories if deleted
3. Run from `task-manager/` using old commands
4. Document issues found
5. Fix issues in new structure
6. Re-test

## Notes

Add any observations or issues encountered during verification:

```
[Your notes here]
```

---

**Completed by:** ________________
**Date:** ________________
**Status:** [ ] Pass [ ] Fail [ ] Needs Review
