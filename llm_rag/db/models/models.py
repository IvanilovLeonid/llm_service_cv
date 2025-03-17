from sqlalchemy import Column, Integer, String, Text
from llm_rag.db.database.database import Base

class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, index=True)
    last_name = Column(String, index=True)
    phone = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    direction = Column(String, index=True)
    skills = Column(Text)
    education = Column(Text)
    experience = Column(Text)
    about_me = Column(Text)