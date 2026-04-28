import os

os.environ["OTEL_SDK_DISABLED"] = "true"

import uuid
from collections.abc import AsyncGenerator

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings
from app.db.models import Tenant

TEST_TENANT_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")


@pytest_asyncio.fixture(scope="session")
def event_loop_policy() -> None:
    # Let pytest-asyncio manage the loop
    return None


@pytest_asyncio.fixture(scope="function")
async def test_tenant_in_db() -> AsyncGenerator[uuid.UUID, None]:
    """
    Seeds the test tenant row required by sessions FK constraint.
    Tears it down after each test.
    """
    engine = create_async_engine(
        settings.database_url,
        pool_pre_ping=True,
    )
    async_session = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        tenant = Tenant(
            id=TEST_TENANT_ID,
            name="Test Tenant",
            tier="DEVELOPER",
            country="NG",
            is_active=True,
        )
        session.add(tenant)
        await session.commit()

    yield TEST_TENANT_ID

    # Cleanup — delete sessions first (FK), then tenant
    async with async_session() as session:
        from sqlalchemy import delete

        from app.db.models import ConsentRecord, Incident
        from app.db.models import Session as DBSession

        await session.execute(
            delete(ConsentRecord).where(ConsentRecord.tenant_id == TEST_TENANT_ID)
        )
        await session.execute(delete(DBSession).where(DBSession.tenant_id == TEST_TENANT_ID))
        await session.execute(delete(Incident).where(Incident.tenant_id == TEST_TENANT_ID))
        await session.execute(delete(Tenant).where(Tenant.id == TEST_TENANT_ID))
        await session.commit()

    await engine.dispose()
