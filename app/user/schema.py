from pydantic import BaseModel, ConfigDict, EmailStr


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserSettingsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    default_currency: str = "USD"
    timezone: str = "UTC"


class UserSettingsUpdate(BaseModel):
    default_currency: str | None = None
    timezone: str | None = None
