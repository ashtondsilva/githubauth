# PostgreSQL Database Configuration

# Database connection parameters
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "github_tokens"
DB_USER = "postgres"
DB_PASSWORD = "postgres"  # Change this to your actual password

# Connection string format for psycopg2
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"