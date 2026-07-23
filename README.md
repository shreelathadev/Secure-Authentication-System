# Moh Secure Auth — Python Developer Internship Assessment

A FastAPI-based Authentication System with JWT login, refresh token rotation, protected routes, secure logout, email OTP verification, password reset, passwordless OTP login, and Google/GitHub social sign-in.

## Tech Stack
FastAPI, SQLAlchemy, Pydantic v2 + pydantic-settings, python-jose (JWT), passlib[bcrypt], httpx (OAuth), SQLite.

## Project Structure
```
app/
├── api/v1/        # Route handlers (auth, users, oauth)
├── auth/          # JWT dependency (get_current_user)
├── models/        # SQLAlchemy models (User, RefreshToken, OTP)
├── schemas/       # Pydantic request/response schemas
├── services/      # Email sending, OTP generation, OAuth calls
├── database/      # DB engine, session
├── core/          # Settings (.env) and security (hashing, JWT)
└── main.py
```

## Quick Setup
1. Clone the repository
2. Create a virtual environment and activate it
3. Install dependencies:
```
   pip install -r requirements.txt
```
4. Copy `.env.example` to `.env`, then generate and paste your own secret key:
```
   python -c "import secrets; print(secrets.token_hex(32))"
```
   (Leave `MAIL_USERNAME` blank — this enables dev mode, where OTP codes print to the terminal instead of needing real email setup.)
5. Run the server:
```
   uvicorn app.main:app --reload
```
6. Open **http://127.0.0.1:8000/docs** in your browser.

## Quick Testing (in this order)
Test each one in Swagger (`/docs`) using "Try it out." Watch your terminal for OTP codes when prompted.

- ✔ **Register** — create a user (`POST /api/v1/auth/register`)
- ✔ **Verify Email** — copy OTP from terminal → `POST /verify-email`
- ✔ **Login** — get access + refresh tokens → `POST /login`
- ✔ **Authorize** — click the padlock icon in Swagger, paste your access token
- ✔ **/users/me** — confirms protected routes work (`GET /api/v1/users/me`)
- ✔ **Refresh** — get a new token pair using your refresh token → `POST /refresh`
- ✔ **Logout** — revoke your refresh token → `POST /logout`
- ✔ **Forgot Password** → **Reset Password** — full password recovery flow
- ✔ **OTP Login** — passwordless login via emailed code
- ✔ *(Optional)* **Google OAuth** / **GitHub OAuth** — visit these directly in a browser tab, not through Swagger (redirects don't work inside Swagger's UI):
```
  http://127.0.0.1:8000/api/v1/oauth/google/login
  http://127.0.0.1:8000/api/v1/oauth/github/login
```
  Requires your own Google Cloud / GitHub OAuth App credentials in `.env` — client secrets are never committed to this repo for security.

## Database
No manual setup needed — tables are created automatically on first run (`Base.metadata.create_all()` in `main.py`). For production, use Alembic:
```
alembic init alembic
alembic revision --autogenerate -m "init"
alembic upgrade head
```

## Security Notes
- Passwords hashed with bcrypt, never stored in plaintext
- Access tokens expire in 15 minutes; refresh tokens rotate on every use and are individually revocable (tracked in DB)
- Logout revokes the specific refresh token server-side, not just client-side
- All secrets loaded from `.env`, nothing hardcoded
- CORS restricted to configured trusted origins

## Testing
```
python -m pytest
```
2 automated tests (registration + login-before-verification) — both passing.

## Bonus Features Status
- Automated test suite: written and passing (2/2)
- Rate limiting: not implemented
- Docker: Dockerfile written, not built/tested in this environment

## Status
All core and advanced features from the assessment brief are implemented and manually verified end-to-end, including live Google and GitHub OAuth sign-in.

## Testing Screenshots
See [SCREENSHOTS.md](./SCREENSHOTS.md) for a full visual walkthrough of every tested flow — registration, JWT login, protected routes, refresh rotation, logout revocation, password reset, OTP login, and both Google and GitHub OAuth sign-in.