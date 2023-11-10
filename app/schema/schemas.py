from pydantic import BaseModel
from typing import Optional


class UserRequest(BaseModel):
    username: str
    password: str
    firstname: Optional[str] = None
    lastname: Optional[str] = None


class UserRequestLogin(BaseModel):
    username: str
    password: str
    totp_code: str


class UserResponse(BaseModel):
    id: Optional[str] = None
    username: str
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    totp_qr_code: Optional[str] = None


class UserProfileRequest(BaseModel):
    user_id: str


class UserProfileResponse(BaseModel):
    username: str
    firstname: str
    lastname: str
