import os
from dotenv import load_dotenv
from sqlmodel import SQLModel, Session, create_engine

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Configurar el motor
engine = create_engine(
     DATABASE_URL,
    echo=False, 
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10
)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

    
def get_session():
    with Session(engine) as session:
        yield session