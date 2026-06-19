from pydantic import BaseModel, ConfigDict


class UserSettingsSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    default_currency: str = "USD"
    timezone: str = "UTC"


class UserSettingsUpdate(BaseModel):
    default_currency: str | None = None
    timezone: str | None = None
