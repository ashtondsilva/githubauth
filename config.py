# PostgreSQL Database Configuration

# Use fixed values for Docker Compose environment
DB_HOST = "postgres-db"  # This matches the service name in docker-compose.yml
DB_PORT = "5432"
DB_NAME = "ardelis"
DB_USER = "austin"
DB_PASSWORD = "12345678"

# Connection string format for psycopg2
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# SQLAlchemy configuration
SQLALCHEMY_DATABASE_URI = DATABASE_URL
