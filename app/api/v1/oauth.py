from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.user import User
from app.core.config import settings
from app.services.oauth_service import google_get_user, github_get_user

router = APIRouter(prefix="/api/v1/oauth", tags=["oauth"])

def _get_or_create_oauth_user(db: Session, provider: str, info: dict) -> User:
    if not info.get("email"):
        raise HTTPException(400, "Email not available from provider")
    user = db.query(User).filter(User.email == info["email"]).first()
    if not user:
        user = User(email=info["email"], full_name=info.get("full_name"),
                     oauth_provider=provider, oauth_id=info["oauth_id"], is_verified=True)
        db.add(user)
        db.commit()
        db.refresh(user)
    return user

@router.get("/google/login")
def google_login():
    url = ("https://accounts.google.com/o/oauth2/v2/auth"
           f"?client_id={settings.GOOGLE_CLIENT_ID}&redirect_uri={settings.GOOGLE_REDIRECT_URI}"
           "&response_type=code&scope=openid%20email%20profile")
    return RedirectResponse(url)

@router.get("/google/callback")
async def google_callback(code: str, db: Session = Depends(get_db)):
    info = await google_get_user(code)
    user = _get_or_create_oauth_user(db, "google", info)
    from app.api.v1.auth import _issue_tokens
    return _issue_tokens(db, user)

@router.get("/github/login")
def github_login():
    url = ("https://github.com/login/oauth/authorize"
           f"?client_id={settings.GITHUB_CLIENT_ID}&redirect_uri={settings.GITHUB_REDIRECT_URI}"
           "&scope=read:user user:email")
    return RedirectResponse(url)

@router.get("/github/callback")
async def github_callback(code: str, db: Session = Depends(get_db)):
    info = await github_get_user(code)
    user = _get_or_create_oauth_user(db, "github", info)
    from app.api.v1.auth import _issue_tokens
    return _issue_tokens(db, user)