from pydantic import BaseModel, EmailStr

class ResumeBase(BaseModel):
    first_name: str
    last_name: str
    phone: str
    email: EmailStr
    direction: str
    skills: str
    education: str
    experience: str
    about_me: str

class ResumeCreate(ResumeBase):
    pass

class ResumeUpdate(ResumeBase):
    pass

class Resume(ResumeBase):
    id: int

    class Config:
        orm_mode = True