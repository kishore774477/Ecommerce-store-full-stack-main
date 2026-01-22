from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config.settings import DB_CONNECTION_STRING

Base = declarative_base()

class Database:
    def __init__(self):
        self.engine = create_engine(DB_CONNECTION_STRING, connect_args={"check_same_thread": False})
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    def get_db(self):
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()

    def init_db(self):
        Base.metadata.create_all(bind=self.engine)

db = Database()
