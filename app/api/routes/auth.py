import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.db.models import Organization, User, UserSession
from app.db.repositories.user_repository import UserRepository
from app.db.session import get_db
from app.storage.redis_client import redis_manager
from app.utils.email_service import OTPService
from app.utils.google_auth import verify_google_id_token
from app.utils.security import create_access_token, create_refresh_token, hash_password, verify_password

PUBLIC_DOMAINS = {"gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "icloud.com", "protonmail.com", "mail.com", "gmx.com", "zoho.com"}


async def _resolve_org_domain(email: str, db: AsyncSession) -> Optional[str]:
    if "@" not in email:
        return None
    raw_domain = email.split("@")[-1].lower()
    if raw_domain in PUBLIC_DOMAINS:
        return None
    stmt = select(Organization).where(Organization.domain == raw_domain)
    res = await db.execute(stmt)
    if res.scalar_one_or_none():
        return f"{raw_domain}-{uuid.uuid4().hex[:6]}"
    return raw_domain


router = APIRouter(prefix="/auth", tags=["Authentication"])


class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    organization_name: str = "Default Enterprise"
    department: str = "Engineering"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class SendOTPRequest(BaseModel):
    email: EmailStr


class VerifyOTPRequest(BaseModel):
    email: EmailStr
    otp: str


class GoogleAuthRequest(BaseModel):
    id_token: str
    organization_name: Optional[str] = "Default Enterprise"
    department: Optional[str] = "General"


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user_id: str
    organization_id: str
    email_verified: bool = True


@router.post("/send-otp")
async def send_otp(req: SendOTPRequest):
    """Send 6-digit OTP code to Gmail address."""
    success, message = await OTPService.create_and_send_otp(req.email)
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return {"success": True, "message": message}


@router.post("/verify-otp", response_model=TokenResponse)
async def verify_otp(req: VerifyOTPRequest, db: AsyncSession = Depends(get_db)):
    """Verify 6-digit OTP code and login/verify user."""
    is_valid = await OTPService.verify_otp(req.email, req.otp)
    if not is_valid:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP code")

    user_repo = UserRepository(db)
    user = await user_repo.get_by_email(req.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not registered. Please register first.")

    user.email_verified = True
    user.last_login = datetime.now(timezone.utc)

    access_token = create_access_token({"sub": str(user.id), "org": str(user.organization_id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})

    user_session = UserSession(
        user_id=user.id,
        refresh_token=refresh_token,
        expires_at=datetime.now(timezone.utc),
    )
    db.add(user_session)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user_id=str(user.id),
        organization_id=str(user.organization_id),
        email_verified=True,
    )


@router.post("/google", response_model=TokenResponse)
async def google_auth(req: GoogleAuthRequest, db: AsyncSession = Depends(get_db)):
    """Authenticate or register user using Google OAuth ID token."""
    g_user = await verify_google_id_token(req.id_token)

    user_repo = UserRepository(db)
    user = await user_repo.get_by_email(g_user["email"])

    if not user:
        org_domain = await _resolve_org_domain(g_user["email"], db)
        org = Organization(
            name=req.organization_name or f"{g_user['name']}'s Org",
            domain=org_domain,
        )
        db.add(org)
        await db.flush()

        user = User(
            organization_id=org.id,
            name=g_user["name"],
            email=g_user["email"],
            password_hash=hash_password(uuid.uuid4().hex),
            auth_provider="google",
            google_sub=g_user["google_sub"],
            email_verified=g_user["email_verified"],
            avatar=g_user["avatar"],
            department=req.department,
            status="active",
        )
        await user_repo.create(user)
    else:
        user.auth_provider = "google"
        user.google_sub = g_user["google_sub"]
        user.email_verified = True
        user.last_login = datetime.now(timezone.utc)
        if g_user["avatar"]:
            user.avatar = g_user["avatar"]

    access_token = create_access_token({"sub": str(user.id), "org": str(user.organization_id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})

    user_session = UserSession(
        user_id=user.id,
        refresh_token=refresh_token,
        expires_at=datetime.now(timezone.utc),
    )
    db.add(user_session)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user_id=str(user.id),
        organization_id=str(user.organization_id),
        email_verified=user.email_verified,
    )


@router.post("/register", response_model=TokenResponse)
async def register(req: RegisterRequest, db: AsyncSession = Depends(get_db)):
    user_repo = UserRepository(db)
    existing_user = await user_repo.get_by_email(req.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    org_domain = await _resolve_org_domain(req.email, db)

    try:
        org = Organization(
            name=req.organization_name,
            domain=org_domain,
        )
        db.add(org)
        await db.flush()

        new_user = User(
            organization_id=org.id,
            name=req.name,
            email=req.email,
            password_hash=hash_password(req.password),
            department=req.department,
            auth_provider="local",
            email_verified=False,
            status="active",
        )
        await user_repo.create(new_user)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Registration failed due to constraint conflict. Email or domain might already be in use.",
        )

    access_token = create_access_token({"sub": str(new_user.id), "org": str(org.id)})
    refresh_token = create_refresh_token({"sub": str(new_user.id)})

    user_session = UserSession(
        user_id=new_user.id,
        refresh_token=refresh_token,
        expires_at=datetime.now(timezone.utc),
    )
    db.add(user_session)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user_id=str(new_user.id),
        organization_id=str(org.id),
        email_verified=False,
    )


@router.post("/login", response_model=TokenResponse)
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    user_repo = UserRepository(db)
    user = await user_repo.get_by_email(req.email)
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    user.last_login = datetime.now(timezone.utc)

    access_token = create_access_token({"sub": str(user.id), "org": str(user.organization_id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})

    user_session = UserSession(
        user_id=user.id,
        refresh_token=refresh_token,
        expires_at=datetime.now(timezone.utc),
    )
    db.add(user_session)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user_id=str(user.id),
        organization_id=str(user.organization_id),
        email_verified=user.email_verified,
    )


@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": str(current_user.id),
        "name": current_user.name,
        "email": current_user.email,
        "organization_id": str(current_user.organization_id),
        "department": current_user.department,
        "auth_provider": getattr(current_user, "auth_provider", "local"),
        "email_verified": getattr(current_user, "email_verified", True),
        "status": current_user.status,
    }
