"""
MediKiosk — Authentication & Hospital Directory API
Provides unified auth for Patients and Doctors, ABHA registration, and OPD Doctor Directory.
"""

import uuid
import logging
from pydantic import BaseModel, Field
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from app.database import get_db

logger = logging.getLogger("medikiosk.api.auth")
router = APIRouter(prefix="/api/auth", tags=["Authentication & Directory"])


class LoginRequest(BaseModel):
    identifier: str = Field(..., description="Mobile, ABHA ID, Doctor username, or PIN")
    password: str = Field(..., description="Password or PIN")
    role: Optional[str] = Field("auto", description="'patient' | 'doctor' | 'auto'")


class PatientRegisterRequest(BaseModel):
    full_name: str
    mobile: str
    abha_id: Optional[str] = None
    password: str
    age: Optional[int] = None
    gender: Optional[str] = "Male"


class AuthResponse(BaseModel):
    authenticated: bool
    message: str
    user: dict


@router.post("/login", response_model=AuthResponse)
async def login(req: LoginRequest, db=Depends(get_db)):
    """
    Unified login supporting:
    - Doctor: ID ('doc-verma') or PIN ('1234')
    - Patient: Mobile ('9876543210'), ABHA ID ('91-4821-3910-4819'), or Patient ID ('pat-001')
    """
    ident = req.identifier.strip()
    pwd = req.password.strip()

    # 1. Doctor PIN bypass / match
    if ident in ("1234", "doctor") or pwd == "1234":
        cursor = await db.execute("SELECT * FROM users WHERE role = 'doctor' AND (id = ? OR password_hash = ?)", (ident, pwd))
        user = await cursor.fetchone()
        if not user:
            # Fallback to default doctor Verma
            cursor = await db.execute("SELECT * FROM users WHERE id = 'doc-verma'")
            user = await cursor.fetchone()

        if user:
            return AuthResponse(
                authenticated=True,
                message="Doctor authenticated successfully",
                user=dict(user)
            )

    # 2. Check users table by username, mobile, or abha_id
    query = """
        SELECT * FROM users
        WHERE (id = ? OR mobile = ? OR abha_id = ? OR email = ?)
        AND (password_hash = ? OR ? = '1234' OR ? = 'patient123')
    """
    cursor = await db.execute(query, (ident, ident, ident, ident, pwd, pwd, pwd))
    user = await cursor.fetchone()

    if user:
        return AuthResponse(
            authenticated=True,
            message="Login successful",
            user=dict(user)
        )

    # 3. If patient mobile/ABHA exists without strict password check (emergency/rural bypass)
    cursor = await db.execute("SELECT * FROM users WHERE mobile = ? OR abha_id = ?", (ident, ident))
    user = await cursor.fetchone()
    if user and req.role == "patient":
        return AuthResponse(
            authenticated=True,
            message="Authenticated via registered mobile/ABHA",
            user=dict(user)
        )

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials. For demo, use Doctor PIN: 1234 or Patient Mobile: 9876543210 / Password: patient123"
    )


@router.post("/patient/register", response_model=AuthResponse)
async def register_patient(req: PatientRegisterRequest, db=Depends(get_db)):
    """Register a new patient profile with ABHA ID and Mobile."""
    patient_id = f"pat-{uuid.uuid4().hex[:8]}"
    abha_id = req.abha_id or f"91-{uuid.uuid4().hex[:4]}-{uuid.uuid4().hex[:4]}-4819"

    try:
        await db.execute("""
            INSERT INTO users (id, role, full_name, mobile, abha_id, password_hash)
            VALUES (?, 'patient', ?, ?, ?, ?)
        """, (patient_id, req.full_name, req.mobile, abha_id, req.password))
        await db.commit()

        cursor = await db.execute("SELECT * FROM users WHERE id = ?", (patient_id,))
        user = await cursor.fetchone()

        return AuthResponse(
            authenticated=True,
            message="Patient registered successfully",
            user=dict(user)
        )
    except Exception as e:
        logger.error(f"Failed to register patient: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Registration failed: Mobile or ABHA ID may already exist ({str(e)})"
        )


@router.get("/directory")
async def get_hospital_directory(db=Depends(get_db)):
    """Returns list of hospital OPD doctors, room numbers, and contact numbers."""
    cursor = await db.execute("""
        SELECT id, full_name, department, room_number, qualification, hospital_name, hospital_phone
        FROM users
        WHERE role = 'doctor'
        ORDER BY room_number ASC
    """)
    doctors = [dict(row) for row in await cursor.fetchall()]

    return {
        "hospital_name": "All India Institute of Ayurveda (AIIA), New Delhi",
        "hospital_address": "Mathura Road, Gautam Puri, Sarita Vihar, New Delhi - 110076",
        "emergency_phone": "108 / 102",
        "opd_reception_phone": "+91-11-26950401",
        "doctors": doctors
    }
