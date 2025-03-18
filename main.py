from fastapi import FastAPI
from llm_rag.backend.http import router
from llm_rag.db.database.database import init_db, Base, engine

# Основное приложение FastAPI
app = FastAPI()

# Инициализация базы данных и создание таблиц при запуске
init_db()
Base.metadata.create_all(bind=engine)

app.include_router(router)

