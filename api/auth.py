"""
Kimlik doğrulama API ve JWT
Roller: admin (tam yetki), user (sadece iş evrakı yazma, diğerleri viewer)
"""
import os
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, HTTPHeader
from pydantic import BaseModel
from jose import JWTError, jwt

from db_instance import db

router = APIRouter(prefix="/api/auth", tags=["auth"])
security = HTTPBearer(auto_error=False)

# JWT ayarları
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "on-muhasebe-default-secret-degistirin")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 gün


class LoginRequest(BaseModel):
    username: str
    password: str


class CreateUserRequest(BaseModel):
    username: str
    password: str
    role: str = "user"  # admin | user


class UserOut(BaseModel):
    id: int
    username: str
    role: str


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    authorization: Optional[str] = HTTPHeader(None),
) -> dict:
    """Bearer token'dan kullanıcı bilgisini döndürür. Geçersizse 401."""
    token = None
    if credentials:
        token = credentials.credentials
    elif authorization and authorization.startswith("Bearer "):
        token = authorization[7:]
    if not token:
        raise HTTPException(status_code=401, detail="Giriş yapılmamış. Lütfen giriş yapın.")
    payload = decode_token(token)
    if not payload or "sub" not in payload or "role" not in payload:
        raise HTTPException(status_code=401, detail="Geçersiz veya süresi dolmuş oturum.")
    return {
        "id": payload.get("id"),
        "username": payload.get("sub"),
        "role": payload.get("role", "user"),
    }


def require_can_write_module(module: str):
    """Sadece yazma yetkisi kontrolü: admin hep True, user sadece is_evraki."""

    async def _check(current_user: dict = Depends(get_current_user)):
        if current_user.get("role") == "admin":
            return current_user
        if current_user.get("role") != "user":
            raise HTTPException(status_code=403, detail="Bu işlem için yetkiniz yok.")
        if module != "is_evraki":
            raise HTTPException(
                status_code=403,
                detail="Bu modülde değişiklik yapma yetkiniz yok. Sadece İş Evrakı modülünde işlem yapabilirsiniz.",
            )
        return current_user

    return _check


def require_admin(current_user: dict = Depends(get_current_user)) -> dict:
    """Sadece admin rolü erişebilir."""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Bu sayfa sadece yönetici (admin) içindir.")
    return current_user


@router.post("/login")
async def login(body: LoginRequest):
    """Kullanıcı adı ve şifre ile giriş. Token ve kullanıcı bilgisi döner."""
    user = db.auth.authenticate(body.username.strip(), body.password)
    if not user:
        raise HTTPException(status_code=401, detail="Kullanıcı adı veya şifre hatalı.")
    token = create_access_token(
        data={
            "sub": user["username"],
            "id": user["id"],
            "role": user.get("role", "user"),
        }
    )
    return {
        "success": True,
        "token": token,
        "user": {"id": user["id"], "username": user["username"], "role": user.get("role", "user")},
    }


@router.get("/me", response_model=dict)
async def me(current_user: dict = Depends(get_current_user)):
    """Giriş yapmış kullanıcı bilgisini döndürür."""
    return {"success": True, "data": current_user}


@router.get("/users")
async def list_users(
    current_user: dict = Depends(require_admin),
):
    """Tüm kullanıcıları listeler (sadece admin)."""
    users = db.auth.list_users()
    return {"success": True, "data": users}


@router.post("/users")
async def create_user(
    body: CreateUserRequest,
    current_user: dict = Depends(require_admin),
):
    """Yeni kullanıcı oluşturur (sadece admin)."""
    role = (body.role or "user").strip().lower()
    if role not in ("admin", "user"):
        raise HTTPException(status_code=400, detail="Rol 'admin' veya 'user' olmalıdır.")
    ok, msg = db.auth.create_user(body.username.strip(), body.password, role)
    if not ok:
        raise HTTPException(status_code=400, detail=msg)
    return {"success": True, "message": msg}
