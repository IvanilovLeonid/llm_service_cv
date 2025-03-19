from pydantic import BaseModel

class ResumeBase(BaseModel):
    full_name: str
    direction: str
    skills: str
    experience: str
    pdf_filename: str

class ResumeCreate(ResumeBase):
    pass

class ResumeUpdate(ResumeBase):
    pass

class Resume(ResumeBase):
    id: int

    class Config:
        orm_mode = True
