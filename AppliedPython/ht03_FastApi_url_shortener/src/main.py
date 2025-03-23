from fastapi import FastAPI
from sqlmodel import SQLModel
from contextlib import asynccontextmanager
from redis import asyncio as aioredis
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
import uvicorn

from database import engine
from config import REDIS_URL
from auth.router import router as auth_router
from links.router import router as links_router

@asynccontextmanager
async def lifespan(_: FastAPI):
    redis = aioredis.from_url(REDIS_URL)
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")

    import auth.schemas
    import links.schemas
    SQLModel.metadata.create_all(engine)
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(auth_router)
app.include_router(links_router)

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True, host="0.0.0.0", log_level="info")
