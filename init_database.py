import sqlalchemy
from sqlalchemy import create_engine
from config import SQLALCHEMY_DATABASE_URI, DB_NAME
from models import Base

def create_database():
    # Create a temporary engine to connect to 'postgres' database
    temp_engine = create_engine(SQLALCHEMY_DATABASE_URI.replace(f'/{DB_NAME}', '/postgres'))
    
    # Check if our database exists and create it if not
    with temp_engine.connect() as conn:
        conn.execute(sqlalchemy.text("COMMIT"))
        
        # Check if database exists
        result = conn.execute(sqlalchemy.text("SELECT 1 FROM pg_catalog.pg_database WHERE datname = :dbname"), {"dbname": DB_NAME})
        exists = result.scalar()
        
        if not exists:
            print(f"Creating database {DB_NAME}...")
            conn.execute(sqlalchemy.text(f"CREATE DATABASE {DB_NAME}"))
            print(f"Database {DB_NAME} created successfully!")
        else:
            print(f"Database {DB_NAME} already exists.")
    
    # Now connect to our database and create tables using SQLAlchemy models
    engine = create_engine(SQLALCHEMY_DATABASE_URI)
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")
    print("Database initialization complete!")

if __name__ == "__main__":
    create_database()