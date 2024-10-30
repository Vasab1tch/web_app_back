from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

DATABASE_URL = "postgresql+asyncpg://postgres:111122@192.168.2.111:5432/postgres"


engine = create_async_engine(DATABASE_URL, echo=True)
Base = declarative_base()

# Функція для отримання сесії
async def get_db() -> AsyncSession:
    async_session = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session

# Функція для створення таблиць
async def create_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
