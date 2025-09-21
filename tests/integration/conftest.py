import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.db.database import Base, get_db_session
from app.db.models import User
from app.main import app


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session", autouse=True)
async def setup_db():
    engine = create_async_engine(
        url="sqlite+aiosqlite:///:memory:", echo=False
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    app.state.test_engine = engine
    yield

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def session():
    engine = app.state.test_engine

    async_session = async_sessionmaker(
        bind=engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as a_s:
        yield a_s


@pytest.fixture
async def client(session: AsyncSession):

    async def override_get_db_session():
        return session

    app.dependency_overrides[get_db_session] = override_get_db_session

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.fixture
async def test_user_1(session: AsyncSession) -> User:
    result = await session.execute(select(User).where(User.api_key == "key_1"))
    user = result.scalar_one_or_none()

    if user is None:
        user = User(name="user_1", api_key="key_1")
        session.add(user)

        await session.commit()
        await session.refresh(user)

    return user


@pytest.fixture
async def test_user_2(session: AsyncSession) -> User:
    result = await session.execute(select(User).where(User.api_key == "key_2"))
    user = result.scalar_one_or_none()

    if user is None:
        user = User(name="user_2", api_key="key_2")

        session.add(user)

        await session.commit()
        await session.refresh(user)

    return user
