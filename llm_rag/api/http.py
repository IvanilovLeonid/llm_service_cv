from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from llm_rag.db.database.database import SessionLocal, engine, Base
from llm_rag.search.search import enhanced_resume_search
from llm_rag.db.schemas.schemas import Resume as ResumeSchema, ResumeCreate, ResumeUpdate, Vacancy as VacancySchema, VacancyCreate, VacancyBase
from llm_rag.db.repository.repository import create_resume, get_resume, get_resumes, update_resume, delete_resume, create_vacancy, get_vacancy, get_vacancies
from pydantic import BaseModel
from typing import List
import requests
import os
import pyttsx3
import threading
import time

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class ResumeWithScore(BaseModel):
    resume: ResumeSchema
    similarity: float


@router.get("/download")
def download_file(file_path: str = Query(...)):
    if os.path.exists(file_path):
        return FileResponse(path=file_path, filename=os.path.basename(file_path), media_type='application/pdf')
    return {"error": "File not found"}


@router.post("/search_resumes/", response_model=List[ResumeWithScore])
def search_resumes(vacancy: VacancyBase, top_n: int = Query(5, ge=1, le=50)):
    """
    Ищет наиболее подходящие резюме под вакансию.
    :param vacancy: JSON с direction и skills
    :param top_n: Сколько лучших резюме вернуть (по умолчанию 5, максимум 50)
    """
    try:
        # Загружаем резюме с другого эндпоинта
        response = requests.get("http://localhost:8000/resumes/")
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Не удалось получить резюме")

        resumes = response.json()

        # Ищем подходящих кандидатов
        results = enhanced_resume_search(vacancy.dict(), resumes)

        # Фильтруем результаты с похожестью >= 5% и сортируем по убыванию
        filtered_results = [
            result for result in results
            if result.get("similarity", 0) >= 0.5
        ]
        filtered_results.sort(key=lambda x: x["similarity"], reverse=True)

        # Ограничиваем top_n
        top_results = filtered_results[:top_n]

        # Формируем ответ
        response_data = [
            ResumeWithScore(resume=result["resume"], similarity=result["similarity"])
            for result in top_results
        ]
        return response_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {e}")


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
