"""Create all database tables in SQLite for local development."""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from app.db.base import Base
from app.db.models import *  # Import all models

async def create_tables():
    sqlite_url = "sqlite+aiosqlite:///./enterprise_rag.db"
    engine = create_async_engine(sqlite_url, echo=True)
    
    async with engine.begin() as conn:
        print("Creating all tables in SQLite...")
        await conn.run_sync(Base.metadata.create_all)
        print("✓ All tables created successfully")
    
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(create_tables())
