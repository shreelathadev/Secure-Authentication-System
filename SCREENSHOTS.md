# Testing Screenshots — Moh Secure Auth

All endpoints were manually tested via Swagger UI (`/docs`) and, for OAuth, directly in the browser. Screenshots below correspond to the testing checklist in the README.

## 1. Available Endpoints (Swagger UI)
![All endpoints](screenshots/Moh-Secure_Auth_HomePage.png)

## 2. Register
![Register request](screenshots/register-user.png)

## 3. Email OTP (dev console output)
![OTP printed in terminal](screenshots/unicorn-log-full-flow.png)

## 4. Login — JWT Access & Refresh Tokens
![Login response](screenshots/login-response-body.png)

## 5. Full Flow Log (register → verify → login → /me → refresh → logout → forgot/reset password → OTP login)
![Terminal log of full flow](screenshots/05-uvicorn-log-full-flow.png)

## 6. Logout — Refresh Token Correctly Revoked
Proof that a refresh token is rejected after logout (`401 Unauthorized`):
![Refresh rejected after logout](screenshots/logout-401.png)

## 7. GitHub OAuth — App Configuration
(Client ID and Secret redacted)
![GitHub OAuth App settings](screenshots/Git-oauth-settings.png)

## 8. GitHub OAuth — Successful Login (Tokens Issued)
![GitHub OAuth callback returning tokens](screenshots/Github_oauth_Login_tokens.png)

## 9. Google OAuth — Consent Screen
![Google sign-in consent](screenshots/Google-OAuth_signIn-consent.png)

## 10. Google OAuth — Account Selection
![Google account chooser](screenshots/Google-OAuth_account-picker.png)