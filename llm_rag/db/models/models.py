from sqlalchemy import Column, Integer, String, Text
from llm_rag.db.database.database import Base


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, index=True)  # ФИО
    direction = Column(String, index=True)  # Направление
    skills = Column(Text)  # Навыки
    experience = Column(Text)  # Опыт работы
    pdf_filename = Column(String)  # Название PDF-файла


class Vacancy(Base):
    __tablename__ = "vacancies"

    id = Column(Integer, primary_key=True, index=True)
    direction = Column(String, index=True)
    skills = Column(Text)
    tasks = Column(Text)