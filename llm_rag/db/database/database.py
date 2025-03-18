import psycopg2
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os

# Строка подключения из переменных окружения или значения по умолчанию
DB_USER = os.getenv("DB_USER", "user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "resumes_db")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Создание подключения
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def init_db():
    """Инициализация базы данных и пользователя при запуске приложения."""
    try:
        # Подключаемся к PostgreSQL через системную базу postgres для создания новой базы
        admin_conn = psycopg2.connect(
            dbname="postgres",
            user="postgres",  # Предполагается, что у вас есть доступ к postgres
            password=os.getenv("PG_ADMIN_PASSWORD", "your_pg_password"),  # Пароль администратора
            host=DB_HOST,
            port=DB_PORT
        )
        admin_conn.autocommit = True
        cursor = admin_conn.cursor()

        # Проверка и создание пользователя
        cursor.execute(f"SELECT 1 FROM pg_roles WHERE rolname = '{DB_USER}'")
        if not cursor.fetchone():
            cursor.execute(f"CREATE USER \"{DB_USER}\" WITH PASSWORD '{DB_PASSWORD}'")

        # Проверка и создание базы данных
        cursor.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{DB_NAME}'")
        if not cursor.fetchone():
            cursor.execute(f"CREATE DATABASE {DB_NAME}")
            cursor.execute(f"GRANT ALL PRIVILEGES ON DATABASE {DB_NAME} TO \"{DB_USER}\"")

        cursor.close()
        admin_conn.close()

        # Подключаемся к созданной базе данных для настройки прав на схему public
        db_conn = psycopg2.connect(
            dbname=DB_NAME,
            user="postgres",
            password=os.getenv("PG_ADMIN_PASSWORD", "your_pg_password"),
            host=DB_HOST,
            port=DB_PORT
        )
        db_conn.autocommit = True
        cursor = db_conn.cursor()

        # Предоставляем пользователю полные права на схему public
        cursor.execute(f"GRANT ALL ON SCHEMA public TO \"{DB_USER}\"")

        # Убеждаемся, что права на создание таблиц и других объектов предоставлены
        cursor.execute(f"ALTER SCHEMA public OWNER TO \"{DB_USER}\"")

        cursor.close()
        db_conn.close()

    except Exception as e:
        print(f"Error initializing database: {e}")