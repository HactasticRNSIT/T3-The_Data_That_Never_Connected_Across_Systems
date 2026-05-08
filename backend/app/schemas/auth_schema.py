from pydantic import BaseModel, EmailStr
from typing import Optional

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: EmailStr
    sector: str
    role: str

class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    user: UserResponse
