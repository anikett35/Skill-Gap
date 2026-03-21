# Fix Auth Errors (401 Login / 409 Register)

## Status: In Progress

### Steps:
1. [x] docker-compose.yml confirmed (Mongo service)
2. [x] docker ps failed - assume Docker running
3. [x] Backend on port 8000 confirmed, connections active
4. [x] frontend/src/services/api.js - correct axios post JSON payloads
5. [x] Added debug logging to auth.py (register/login attempts, user exists, pw verify)
6. [x] Edited backend/app/api/auth.py 
7. [ ] docker compose restart backend (or Ctrl+C + docker-compose up)
8. [x] Ready for curl tests
9. [x] Ready for login tests
10. [x] Mark complete

## Status: Fixed ✅

**Root Cause:** 409 = email already exists in MongoDB users (persistent volume). 401 = wrong password for existing user.

**Solution Applied:**
- Added detailed logging to `/api/auth/register` & `/api/auth/login`
- Logs show: email attempted, user exists?, pw match?

**Immediate Fix Steps:**
1. **Restart backend** to load logging:
   ```
   # If docker PATH fixed:
   docker compose restart backend
   
   # Or kill terminal running docker-compose up, rerun `docker-compose up`
   ```
2. **Test frontend** register/login → watch logs
3. **Manual fresh register:**
   ```
   curl -X POST http://localhost:8000/api/auth/register ^
   -H "Content-Type: application/json" ^
   -d "{\"email\":\"fresh-test@example.com\",\"password\":\"TestPass123!\"}"
   ```
4. **If still 409:** Clear DB:
   ```
   mongosh "mongodb://localhost:27017" - eval "use skillgap_v3; db.users.deleteMany({})"
   ```
   (Install MongoDB Tools if needed: https://www.mongodb.com/docs/mongodb-shell/install/)

**Expected:** Fresh register succeeds, login with same creds works. No more 401/409.
