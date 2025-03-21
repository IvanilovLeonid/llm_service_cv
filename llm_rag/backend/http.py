from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from llm_rag.db.database.database import SessionLocal, engine, Base
from llm_rag.db.schemas.schemas import Resume as ResumeSchema, ResumeCreate, ResumeUpdate, Vacancy as VacancySchema, VacancyCreate
from llm_rag.db.repository.repository import create_resume, get_resume, get_resumes, update_resume, delete_resume, create_vacancy, get_vacancy, get_vacancies

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


@router.post("/vacancies/", response_model=VacancySchema)
def create_vacancy_api(vacancy: VacancyCreate, db: Session = Depends(get_db)):
    return create_vacancy(db=db, vacancy=vacancy)


@router.get("/vacancies/{vacancy_id}", response_model=VacancySchema)
def read_vacancy(vacancy_id: int, db: Session = Depends(get_db)):
    db_vacancy = get_vacancy(db, vacancy_id=vacancy_id)
    if db_vacancy is None:
        raise HTTPException(status_code=404, detail="Vacancy not found")
    return db_vacancy


@router.get("/vacancies/", response_model=list[VacancySchema])
def read_vacancies(db: Session = Depends(get_db)):
    return get_vacancies(db)
