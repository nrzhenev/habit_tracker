from typing import Any

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import bearer_scheme, decode_token
from app.database import get_db
from app.models.user import User


def _require_credential(param: Any):
    if param is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    payload = decode_token(credentials.credentials)
    _require_credential(payload)

    user_id = payload.get("sub")
    _require_credential(user_id)
    try:
        parsed_id = int(user_id)
    except (ValueError, TypeError):
        _require_credential(None)

    result = await db.execute(select(User).where(User.id == parsed_id))
    user = result.scalar_one_or_none()
    _require_credential(user)

    return user
