from fastapi import FastAPI, HTTPException, Header, Response, APIRouter
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy.future import select  # SQLAlchemy 1.4 이상에서 비동기 쿼리 사용
from database.core import AsyncSessionLocal
from database.user import User
from database.application import Application
from database.department import Department
from tools import check_auth  # check_auth가 비동기 함수라고 가정

router = APIRouter()

class ApplicationExample(BaseModel):
    bio: str
    motive: str
    plan: str
    which_department: str

@router.post("/api/application", tags=["application"])
async def submit_apply(data: ApplicationExample, token: str = Header(...)):
    user = check_auth(token)  
    
    if not user:
        raise HTTPException(status_code=401, detail="로그인 후 이용 가능합니다.")
    
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.id == user))
        user_info = result.scalars().first()  
    
    if user_info and user_info.is_submitted:
        raise HTTPException(status_code=400, detail="이미 제출하셨습니다.")

    
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Department).where(Department.name == data.which_department))
        department_info = result.scalars().first()  
    if not department_info:
        raise HTTPException(status_code=404, detail="존재하지 않는 부서입니다.")

    db_value = Application(
        bio=data.bio,
        motive=data.motive,
        plan=data.plan,
        department_id=department_info.id, 
        user_id=user,
        last_modified=datetime.now()
    )
    
    async with AsyncSessionLocal() as session:
        session.add(db_value)
        await session.commit()

    return {"ok": True}
