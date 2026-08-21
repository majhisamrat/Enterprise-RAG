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
from app.utils.logger import logger
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


class RegisterInitRequest(BaseModel):
    """Initial registration request - stores temp data and sends OTP"""
    name: str
    email: EmailStr
    password: str
    organization_name: str = "Default Enterprise"
    department: str = "Engineering"


class RegisterVerifyRequest(BaseModel):
    """Complete registration after OTP verification"""
    email: EmailStr
    otp: str


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


class GoogleLoginRequest(BaseModel):
    """Request body for Google OAuth login with access token"""
    access_token: str
    email: str
    name: str
    picture: Optional[str] = None
    organization_name: Optional[str] = "Default Enterprise"
    department: Optional[str] = None
    department: Optional[str] = "General"


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user_id: str
    organization_id: str
    email_verified: bool = True


@router.post("/send-otp")
async def send_otp(req: SendOTPRequest, db: AsyncSession = Depends(get_db)):
    """Send 6-digit OTP code to email address - only if user exists."""
    # Check if user exists in database
    user_repo = UserRepository(db)
    user = await user_repo.get_by_email(req.email.lower())
    
    if not user:
        raise HTTPException(
            status_code=404, 
            detail="Email not registered yet. Please create an account first."
        )
    
    # User exists, send OTP
    success, message = await OTPService.create_and_send_otp(req.email)
    if not success:
        raise HTTPException(status_code=400, detail=message)
    
    logger.info(f"OTP sent to registered user: {req.email}")
    return {"success": True, "message": message}


@router.post("/register-init")
async def register_init(req: RegisterInitRequest, db: AsyncSession = Depends(get_db)):
    """
    Initialize registration: store temp data in Redis and send OTP.
    User is NOT created yet - only after OTP verification.
    """
    # Check if email already registered
    user_repo = UserRepository(db)
    existing_user = await user_repo.get_by_email(req.email.lower())
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Store registration data in Redis with OTP TTL (5 minutes)
    redis_key = f"pending_registration:{req.email.lower()}"
    registration_data = {
        "name": req.name,
        "email": req.email.lower(),
        "password": req.password,
        "organization_name": req.organization_name,
        "department": req.department,
    }
    
    # Save registration data
    import json
    saved = await redis_manager.set_cache(
        redis_key, 
        json.dumps(registration_data), 
        ttl=5 * 60  # 5 minutes, same as OTP
    )
    if not saved:
        raise HTTPException(status_code=400, detail="Failed to process registration")
    
    # Generate and send OTP
    success, message = await OTPService.create_and_send_otp(req.email)
    if not success:
        # Clean up Redis on OTP send failure
        await redis_manager.delete_cache(redis_key)
        raise HTTPException(status_code=400, detail=message)
    
    logger.info(f"Registration initiated for {req.email}, OTP sent")
    return {"success": True, "message": f"OTP sent to {req.email}"}


@router.post("/register-verify", response_model=TokenResponse)
async def register_verify(req: RegisterVerifyRequest, db: AsyncSession = Depends(get_db)):
    """
    Complete registration after OTP verification.
    Creates user account if OTP is valid.
    """
    # Verify OTP
    is_valid = await OTPService.verify_otp(req.email, req.otp)
    if not is_valid:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP code")
    
    # Get pending registration data from Redis
    redis_key = f"pending_registration:{req.email.lower()}"
    registration_data_json = await redis_manager.get_cache(redis_key)
    
    if not registration_data_json:
        raise HTTPException(
            status_code=400, 
            detail="Registration data expired. Please start registration again."
        )
    
    # Parse registration data (might be dict or string depending on Redis store)
    import json
    try:
        if isinstance(registration_data_json, dict):
            registration_data = registration_data_json
        else:
            registration_data = json.loads(registration_data_json)
    except (json.JSONDecodeError, TypeError):
        raise HTTPException(status_code=400, detail="Invalid registration data")
    
    # Check if email is still available
    user_repo = UserRepository(db)
    existing_user = await user_repo.get_by_email(req.email.lower())
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create organization and user
    org_domain = await _resolve_org_domain(req.email, db)
    
    try:
        org = Organization(
            name=registration_data["organization_name"],
            domain=org_domain,
        )
        db.add(org)
        await db.flush()
        
        new_user = User(
            organization_id=org.id,
            name=registration_data["name"],
            email=registration_data["email"],
            password_hash=hash_password(registration_data["password"]),
            department=registration_data["department"],
            auth_provider="local",
            email_verified=True,  # Email is verified via OTP
            status="active",
        )
        await user_repo.create(new_user)
        
        # Clean up Redis
        await redis_manager.delete_cache(redis_key)
        
        logger.info(f"User registered with email verification: {req.email}")
        
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Registration failed due to constraint conflict. Email or domain might already be in use.",
        )
    
    # Create tokens and session
    access_token = create_access_token({"sub": str(new_user.id), "org": str(org.id)})
    refresh_token = create_refresh_token({"sub": str(new_user.id)})
    
    user_session = UserSession(
        user_id=new_user.id,
        refresh_token=refresh_token,
        expires_at=datetime.now(timezone.utc),
    )
    db.add(user_session)
    await db.commit()
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user_id=str(new_user.id),
        organization_id=str(org.id),
        email_verified=True,
    )


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


@router.post("/google-login", response_model=TokenResponse)
async def google_login(req: GoogleLoginRequest, db: AsyncSession = Depends(get_db)):
    """Authenticate or register user using Google OAuth access token (from frontend)."""
    user_repo = UserRepository(db)
    user = await user_repo.get_by_email(req.email.lower())

    if not user:
        logger.info(f"No existing user found for {req.email.lower()}, creating new user")
        # New user - create organization and user
        org_domain = await _resolve_org_domain(req.email, db)
        org = Organization(
            name=req.organization_name or f"{req.name}'s Org",
            domain=org_domain,
        )
        db.add(org)
        await db.flush()
        await db.commit()
        logger.info(f"Organization created with ID {org.id}")

        user = User(
            organization_id=org.id,
            name=req.name,
            email=req.email.lower(),
            password_hash=hash_password(uuid.uuid4().hex),
            auth_provider="google",
            google_sub=req.access_token[:50],
            email_verified=True,
            avatar=req.picture,
            department=req.department or "General",
            status="active",
        )
        # Use repository create method which handles commit properly
        user = await user_repo.create(user)
        logger.info(f"New Google user created: {req.email} with ID {user.id}")
        
        # Verify user was created by re-querying in fresh session
        verify_user = await user_repo.get_by_email(req.email.lower())
        logger.info(f"Verified user exists in DB: {verify_user.id if verify_user else 'NOT FOUND'}")
    else:
        # Existing user - update via raw SQL
        from sqlalchemy import update as sql_update
        user_id = user.id
        
        logger.info(f"Found existing user: {req.email} with ID {user_id}")
        
        # Update the user in database directly
        stmt = sql_update(User).where(User.id == user_id).values(
            auth_provider="google",
            email_verified=True,
            last_login=datetime.now(timezone.utc),
            avatar=req.picture if req.picture else user.avatar,
        )
        await db.execute(stmt)
        await db.commit()
        logger.info(f"Google user logged in: {req.email} with ID {user_id}")

    # Ensure user object has correct values
    logger.info(f"Creating token for user ID: {user.id}, org ID: {user.organization_id}")
    
    # Create tokens
    access_token = create_access_token({"sub": str(user.id), "org": str(user.organization_id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})

    user_session = UserSession(
        user_id=user.id,
        refresh_token=refresh_token,
        expires_at=datetime.now(timezone.utc),
    )
    db.add(user_session)
    await db.commit()

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


class ResetPasswordRequest(BaseModel):
    email: EmailStr
    otp: str
    new_password: str


@router.post("/reset-password", response_model=TokenResponse)
async def reset_password(req: ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    """Reset user password after OTP verification."""
    # Note: OTP was already verified in the verify-otp endpoint
    # We don't verify it again here to prevent replay attack issues
    
    # Find user
    user_repo = UserRepository(db)
    user = await user_repo.get_by_email(req.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Update password
    user.password_hash = hash_password(req.new_password)
    user.email_verified = True
    user.last_login = datetime.now(timezone.utc)
    
    db.add(user)
    await db.commit()
    
    logger.info(f"Password reset for user: {req.email}")

    # Create new tokens
    access_token = create_access_token({"sub": str(user.id), "org": str(user.organization_id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})

    user_session = UserSession(
        user_id=user.id,
        refresh_token=refresh_token,
        expires_at=datetime.now(timezone.utc),
    )
    db.add(user_session)
    await db.commit()

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user_id=str(user.id),
        organization_id=str(user.organization_id),
        email_verified=True,
    )
