# Moh Secure Auth — Python Developer Internship Assessment

A production-style Authentication System built with **FastAPI**, covering registration, JWT-based login with refresh token rotation, protected routes, secure logout, email OTP verification, password reset, passwordless OTP login, and social sign-in via Google and GitHub.

## Tech Stack
- **FastAPI** — API framework
- **SQLAlchemy** — ORM / database models
- **Pydantic v2 + pydantic-settings** — request/response validation and `.env` config
- **python-jose** — JWT encoding/decoding
- **passlib[bcrypt]** — password hashing
- **httpx** — OAuth token exchange with Google/GitHub
- **SQLite** — database (swap `DATABASE_URL` for Postgres/MySQL in production)

## Project Structure
```
app/
├── api/v1/        # Route handlers (auth, users, oauth)
├── auth/          # JWT dependency injection (get_current_user)
├── models/        # SQLAlchemy models (User, RefreshToken, OTP)
├── schemas/       # Pydantic request/response schemas
├── services/      # Email sending, OTP generation, OAuth provider calls
├── database/      # Engine, session, Base
├── core/          # Settings (.env) and security (hashing, JWT)
└── main.py        # App entrypoint, router registration, CORS
```

## Setup

```bash
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

pip install -r requirements.txt
copy .env.example .env       # Windows
# cp .env.example .env       # macOS/Linux
```

Generate a secret key and paste it into `.env`:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Leave `MAIL_USERNAME` blank in `.env` for local testing — this triggers a dev-mode fallback that **prints OTP codes to the terminal** instead of requiring real SMTP credentials.

For social sign-in, add your own Google Cloud OAuth and GitHub OAuth App credentials to `.env` (`GOOGLE_CLIENT_ID/SECRET`, `GITHUB_CLIENT_ID/SECRET`) with redirect URIs set to:
```
http://localhost:8000/api/v1/oauth/google/callback
http://localhost:8000/api/v1/oauth/github/callback
```

Run the server:
```bash
uvicorn app.main:app --reload
```

Tables are created automatically on startup via `Base.metadata.create_all()`. For production, use Alembic migrations instead:
```bash
alembic init alembic
# in alembic/env.py: set target_metadata = Base.metadata, import from app.database.database
alembic revision --autogenerate -m "init"
alembic upgrade head
```

## API Testing

Interactive Swagger docs: **http://127.0.0.1:8000/docs**

> Note: OAuth login/callback endpoints (`/oauth/google/login`, `/oauth/github/login`) involve real browser redirects and should be tested by visiting the URL directly in a browser tab, not via Swagger's "Try it out" button, since Swagger's AJAX calls don't follow cross-origin redirects.

### Example flows (curl)

**Register**
```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"Passw0rd1","full_name":"Test User"}'
```

**Verify email** (OTP printed in server terminal)
```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/verify-email \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","code":"123456"}'
```

**Login**
```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=Passw0rd1"
```

**Access a protected route**
```bash
curl http://127.0.0.1:8000/api/v1/users/me \
  -H "Authorization: Bearer <access_token>"
```

**Refresh token (rotates old refresh token)**
```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token":"<refresh_token>"}'
```

**Logout (revokes refresh token)**
```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/logout \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"refresh_token":"<refresh_token>"}'
```

**Forgot / reset password**
```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/forgot-password \
  -H "Content-Type: application/json" -d '{"email":"user@example.com"}'

curl -X POST http://127.0.0.1:8000/api/v1/auth/reset-password \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","code":"123456","new_password":"NewPass456"}'
```

**Passwordless OTP login**
```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/otp-login/request \
  -H "Content-Type: application/json" -d '{"email":"user@example.com"}'

curl -X POST http://127.0.0.1:8000/api/v1/auth/otp-login/verify \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","code":"123456"}'
```

**Social sign-in** — visit directly in a browser:
```
http://127.0.0.1:8000/api/v1/oauth/google/login
http://127.0.0.1:8000/api/v1/oauth/github/login
```

## Security Notes
- Passwords hashed with bcrypt (via passlib), never stored or logged in plaintext
- Access tokens are short-lived (15 min); refresh tokens are rotated on every use and tracked in the database so a used/stolen refresh token can be individually revoked
- Logout revokes the specific refresh token server-side (not just client-side token deletion)
- All secrets and credentials are loaded from `.env`, never hardcoded
- CORS is restricted to configured trusted origins via `CORS_ORIGINS`

## Testing
A pytest suite is included in `tests/test_auth.py` covering registration and login-before-verification behavior. (Not yet run in this environment — bonus scope.)

## Bonus Features Status
- Rate limiting: not implemented
- Automated test suite: written, not executed
- Docker: Dockerfile written, not built/tested

## Status
All core and advanced features from the assessment brief are implemented and manually verified end-to-end, including both Google and GitHub OAuth flows against live provider sign-in.