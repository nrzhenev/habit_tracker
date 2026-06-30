from datetime import datetime
from zoneinfo import ZoneInfo

from app.user.schema import UserSettingsSchema


def current_time(user_settings: UserSettingsSchema) -> str:
    tz = ZoneInfo(user_settings.timezone)
    return datetime.now(tz).isoformat()


def current_datetime(user_settings: UserSettingsSchema) -> datetime:
    return datetime.now(ZoneInfo(user_settings.timezone))
