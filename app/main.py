from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.base import Base
from app.db.session import engine
from app.user.auth import router as auth_router
from app.activity.router import router as activities_router
from app.entry.router import router as entries_router
from app.event.router import router as events_router
from app.expense.router import router as expenses_router
from app.user.router import router as users_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


def get_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(users_router)
    app.include_router(auth_router)
    app.include_router(entries_router)
    app.include_router(expenses_router)
    app.include_router(activities_router)
    app.include_router(events_router)

    return app


app = get_app()
