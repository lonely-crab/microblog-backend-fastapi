from fastapi import Header, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import AsyncGenerator

from app.db.database import get_db_session
from app.db.models import User


async def get_current_user(api_key: str = Header(...), session: AsyncSession = Depends(get_db_session)):
    """
    Authentification function for users via API key.
    """
    result = await session.execute(select(User).where(User.api_key == api_key))
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(status_code=403, detail="Invalid API key")
    
    return user
