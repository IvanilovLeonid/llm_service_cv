from sqlalchemy.orm import Session
from llm_rag.db.models.models import Resume
from llm_rag.db.schemas.schemas import ResumeCreate, ResumeUpdate

def create_resume(db: Session, resume: ResumeCreate):
    db_resume = Resume(**resume.dict())
    db.add(db_resume)
    db.commit()
    db.refresh(db_resume)
    return db_resume

def get_resume(db: Session, resume_id: int):
    return db.query(Resume).filter(Resume.id == resume_id).first()

def get_resumes(db: Session):
    return db.query(Resume).all()

def update_resume(db: Session, resume_id: int, resume: ResumeUpdate):
    db_resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not db_resume:
        return None
    for key, value in resume.dict().items():
        setattr(db_resume, key, value)
    db.commit()
    db.refresh(db_resume)
    return db_resume

def delete_resume(db: Session, resume_id: int):
    db_resume = db.query(Resume).filter(Resume.id == resume_id).first()
    if not db_resume:
        return None
    db.delete(db_resume)
    db.commit()
    return {"message": "Resume deleted"}
