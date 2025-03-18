from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from llm_rag.db.database.database import SessionLocal, engine, Base
from llm_rag.db.schemas.schemas import Resume as ResumeSchema, ResumeCreate, ResumeUpdate
from llm_rag.db.repository.repository import create_resume, get_resume, get_resumes, update_resume, delete_resume

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/resumes/", response_model=ResumeSchema)
def create_resume_api(resume: ResumeCreate, db: Session = Depends(get_db)):
    return create_resume(db=db, resume=resume)

@router.get("/resumes/{resume_id}", response_model=ResumeSchema)
def read_resume(resume_id: int, db: Session = Depends(get_db)):
    db_resume = get_resume(db, resume_id=resume_id)
    if db_resume is None:
        raise HTTPException(status_code=404, detail="Resume not found")
    return db_resume

@router.get("/resumes/", response_model=list[ResumeSchema])
def read_resumes(db: Session = Depends(get_db)):
    return get_resumes(db)

@router.put("/resumes/{resume_id}", response_model=ResumeSchema)
def update_resume_api(resume_id: int, resume: ResumeUpdate, db: Session = Depends(get_db)):
    return update_resume(db, resume_id, resume)

@router.delete("/resumes/{resume_id}")
def delete_resume_api(resume_id: int, db: Session = Depends(get_db)):
    return delete_resume(db, resume_id)