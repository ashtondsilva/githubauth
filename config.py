# PostgreSQL Database Configuration

# Database connection parameters
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "ardelis"
DB_USER = "ashton"
DB_PASSWORD = "12345678"  # Change this to your actual password

# Connection string format for psycopg2
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# SQLAlchemy configuration
SQLALCHEMY_DATABASE_URI = DATABASE_URL
SQLALCHEMY_TRACK_MODIFICATIONS = False