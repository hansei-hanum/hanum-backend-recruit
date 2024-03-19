from fastapi import FastAPI, HTTPException, Header, Response, APIRouter, Depends
from pydantic import BaseModel
from datetime import datetime
from depends import RequireAuth
from sqlalchemy.future import select 
from sqlalchemy.sql.expression import desc
from database.core import AsyncSessionLocal
from database.user import User
from database.application import Application
from database.department import Department
from tools import check_auth  

router = APIRouter()

class ApplicationExample(BaseModel):
    bio: str
    motive: str
    plan: str
    which_department: str

@router.post("/api/application", tags=["application"])
async def submit_apply(data: ApplicationExample, userid=Depends(RequireAuth)):
    
    if not userid:
        raise HTTPException(status_code=401, message="로그인 후 이용 가능합니다.")
    
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Application).order_by(desc(Application.id)))
        apply_info = result.scalars().first()
    
        if apply_info and apply_info.is_submitted:
            raise HTTPException(status_code=401, message="이미 제출하셨습니다.")
            
        if apply_info:
            apply_info.bio = data.bio
            apply_info.motive = data.motive
            apply_info.plan = data.plan
            apply_info.last_modified = datetime.now()
            
            session.add(apply_info)
            await session.commit()
            return {"message": "success"}

        result = await session.execute(select(Department).where(Department.name == data.which_department))
        department_info = result.scalars().first()  
        
        if not department_info:
            raise HTTPException(status_code=404, message="존재하지 않는 부서입니다.")

        db_value = Application(
            bio=data.bio,
            motive=data.motive,
            plan=data.plan,
            department_id=department_info.id, 
            user_id=userid,
            last_modified=datetime.now()
        )
    
        session.add(db_value)
        await session.commit()

    return {"ok": True}