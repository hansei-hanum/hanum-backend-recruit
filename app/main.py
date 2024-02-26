from fastapi import FastAPI, Header
from pathlib import Path
from database.core import async_engine, Base  # Base를 여기서 임포트합니다.
from routes import include_router
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession  # 필요한 비동기 함수를 임포트합니다.

app = FastAPI()

from tools import check_auth  # check_auth 함수를 임포트합니다.

from routes.application import *
from routes.user import *

# 라우터를 임포트합니다.
from routes.user import router as user_router
from routes.application import router as application_router

# 데이터베이스 테이블을 비동기적으로 생성합니다.
async def create_tables():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# 라우터를 애플리케이션에 포함시킵니다.
# app.include_router(user_router)
# app.include_router(application_router)

@app.post("/api/authcheck", tags=["authcheck test"])
async def authcheck(token : str = Header(...)):
    user = check_auth(token)
    
    if not user:
        return {"ok": "False"}
    
    return {"received_token": token}

include_router(app)
