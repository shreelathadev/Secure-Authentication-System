from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.user import User
from app.models.token import RefreshToken
from app.models.otp import OTP
from app.schemas.user import UserCreate, UserOut
from app.schemas.token import TokenPair, RefreshRequest, LogoutRequest
from app.schemas.otp import OTPRequest, OTPVerify, PasswordReset
from app.core.security import (
    hash_password, verify_password, create_access_token,
    create_refresh_token, decode_token,
)
from app.services.email_service import generate_otp, send_email
from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

def _issue_tokens(db: Session, user: User) -> TokenPair:
    access = create_access_token(user.email)
    refresh, jti, expires_at = create_refresh_token(user.email)
    db.add(RefreshToken(user_id=user.id, jti=jti, expires_at=expires_at))
    db.commit()
    return TokenPair(access_token=access, refresh_token=refresh)

@router.post("/register", response_model=UserOut, status_code=201)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(400, "Email already registered")
    user = User(
        email=payload.email,
        hashed_password=hash_password(payload.password),
        full_name=payload.full_name,
        is_verified=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    code = generate_otp()
    db.add(OTP(email=user.email, code=code, purpose="verify_email",
               expires_at=datetime.utcnow() + timedelta(minutes=10)))
    db.commit()
    send_email(user.email, "Verify your email", f"Your verification code is {code}")
    return user

@router.post("/verify-email")
def verify_email(payload: OTPVerify, db: Session = Depends(get_db)):
    otp = _consume_valid_otp(db, payload.email, payload.code, "verify_email")
    user = db.query(User).filter(User.email == payload.email).first()
    user.is_verified = True
    db.commit()
    return {"message": "Email verified"}

@router.post("/login", response_model=TokenPair)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not user.hashed_password or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Incorrect email or password")
    if not user.is_verified:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Email not verified")
    return _issue_tokens(db, user)

@router.post("/refresh", response_model=TokenPair)
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)):
    data = decode_token(payload.refresh_token)
    if not data or data.get("type") != "refresh":
        raise HTTPException(401, "Invalid refresh token")
    stored = db.query(RefreshToken).filter(RefreshToken.jti == data["jti"]).first()
    if not stored or stored.revoked or stored.expires_at < datetime.utcnow():
        raise HTTPException(401, "Refresh token expired or revoked")
    user = db.query(User).filter(User.email == data["sub"]).first()
    stored.revoked = True  # rotation: old refresh token is now dead
    db.commit()
    return _issue_tokens(db, user)

@router.post("/logout")
def logout(payload: LogoutRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    data = decode_token(payload.refresh_token)
    if data and data.get("type") == "refresh":
        stored = db.query(RefreshToken).filter(RefreshToken.jti == data["jti"]).first()
        if stored:
            stored.revoked = True
            db.commit()
    return {"message": "Logged out"}

@router.post("/forgot-password")
def forgot_password(payload: OTPRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if user:
        code = generate_otp()
        db.add(OTP(email=payload.email, code=code, purpose="password_reset",
                   expires_at=datetime.utcnow() + timedelta(minutes=10)))
        db.commit()
        send_email(payload.email, "Password reset code", f"Your reset code is {code}")
    return {"message": "If that email exists, a reset code has been sent"}

@router.post("/reset-password")
def reset_password(payload: PasswordReset, db: Session = Depends(get_db)):
    _consume_valid_otp(db, payload.email, payload.code, "password_reset")
    user = db.query(User).filter(User.email == payload.email).first()
    user.hashed_password = hash_password(payload.new_password)
    db.commit()
    return {"message": "Password reset successful"}

@router.post("/otp-login/request")
def otp_login_request(payload: OTPRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if user:
        code = generate_otp()
        db.add(OTP(email=payload.email, code=code, purpose="login",
                   expires_at=datetime.utcnow() + timedelta(minutes=5)))
        db.commit()
        send_email(payload.email, "Your login code", f"Your one-time login code is {code}")
    return {"message": "If that email exists, a login code has been sent"}

@router.post("/otp-login/verify", response_model=TokenPair)
def otp_login_verify(payload: OTPVerify, db: Session = Depends(get_db)):
    _consume_valid_otp(db, payload.email, payload.code, "login")
    user = db.query(User).filter(User.email == payload.email).first()
    return _issue_tokens(db, user)

def _consume_valid_otp(db: Session, email: str, code: str, purpose: str) -> OTP:
    otp = (
        db.query(OTP)
        .filter(OTP.email == email, OTP.code == code, OTP.purpose == purpose, OTP.is_used == False)
        .order_by(OTP.created_at.desc())
        .first()
    )
    if not otp or otp.expires_at < datetime.utcnow(): 
        raise HTTPException(400, "Invalid or expired code")
    otp.is_used = True
    db.commit()
    return otp