from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.database import get_db
from app.models.user import User
from app.models.user_settings import UserSettings
from app.schemas.user_settings import UserSettingsSchema, UserSettingsUpdate

router = APIRouter(tags=["users"])


@router.get("/me")
async def get_me(user: User = Depends(get_current_user)):
    return {"id": user.id, "email": user.email}


@router.patch("/me/settings", response_model=UserSettingsSchema)
async def update_settings(
    body: UserSettingsUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(UserSettings).where(UserSettings.user_id == user.id)
    )
    settings = result.scalar_one_or_none()

    if settings is None:
        settings = UserSettings(user_id=user.id)
        db.add(settings)

    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(settings, field, value)

    await db.commit()
    await db.refresh(settings)
    return settings
