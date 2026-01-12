# Backend Health Checklist

Use this checklist to verify the backend is production-ready and functional.

## 1. Startup Checks
- [ ] Virtual Environment is active (`venv`).
- [ ] Dependencies are installed (`pip install -r requirements.txt`).
- [ ] `uvicorn main:app --reload` starts without any "ImportError" or "SyntaxError".
- [ ] Database file `sql_app.db` is created automatically.
- [ ] "INFO: Application startup complete" appears in logs.

## 2. API Reachability
- [ ] `GET http://localhost:8000/docs` loads the Swagger UI.
- [ ] `GET /openapi.json` returns valid JSON.
- [ ] CORS is configured to allow requests from the Frontend (Port 5500/LiveServer).

## 3. Database Integrity
- [ ] `models.Base.metadata.create_all` runs on startup.
- [ ] Tables `master_users`, `business_users`, `messages`, `credit_transactions` exist.
- [ ] IDs are generating as UUID strings (e.g., "550e8400-e29b-...").

## 4. Feature Logic
- [ ] **Reseller Creation**: Can create a Reseller via POST. Returns ID.
- [ ] **Auth/Config**: Can create `WhatsAppOfficialConfig` for a user.
- [ ] **Credits**:
    - [ ] Distributing credits reduces Reseller balance.
    - [ ] Distributing credits increases Business User balance.
    - [ ] Transaction is recorded in `credit_transactions`.
- [ ] **Messaging**:
    - [ ] Sending checks balance first.
    - [ ] Sending Deducts balance.
    - [ ] Usage Log is created.

## 5. Error Handling
- [ ] Invalid IDs return `404 Not Found`.
- [ ] Insufficient funds return `400 Bad Request`.
- [ ] Duplicate emails/usernames return `400 Bad Request`.
- [ ] Server errors return `500` (not crashing the app).
