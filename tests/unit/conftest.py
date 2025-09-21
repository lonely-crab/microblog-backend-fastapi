import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.db.database import Base
from app.db.models import Media, Tweet, User


# so it doesn't run on trio backend and only on asyncio
@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def session():
    engine = create_async_engine(url="sqlite+aiosqlite:///:memory:", echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = async_sessionmaker(
        bind=engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as a_s:
        yield a_s

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def test_user_1(session: AsyncSession) -> User:
    user = User(name="user_1", api_key="key_1")

    session.add(user)

    await session.commit()
    await session.refresh(user)

    return user


@pytest.fixture
async def test_user_2(session: AsyncSession) -> User:
    user = User(name="user_2", api_key="key_2")

    session.add(user)

    await session.commit()
    await session.refresh(user)

    return user


@pytest.fixture
async def test_tweet_1(session: AsyncSession, test_user_1: User) -> Tweet:
    tweet = Tweet(content="string_1", author_id=test_user_1.id)

    session.add(tweet)

    await session.commit()
    await session.refresh(tweet)

    return tweet


@pytest.fixture
async def test_media_1(session: AsyncSession) -> Media:
    media = Media(file_path="/media/test.jpg", tweet_id=None)

    session.add(media)

    await session.commit()
    await session.refresh(media)

    return media
