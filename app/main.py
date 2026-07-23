from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database.database import Base, engine
from app.core.config import settings
from app.api.v1 import auth, users, oauth
from app.models import user, token, otp  # noqa: ensures tables are registered

Base.metadata.create_all(bind=engine)  # fine for dev; use Alembic for production migrations

app = FastAPI(title="MOH Technology Secure Auth System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(oauth.router)

@app.get("/")
def health():
    return {"status": "ok"}