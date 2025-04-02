# GitHub OAuth App with PostgreSQL

This application allows users to authenticate with GitHub OAuth and manage their GitHub repositories. It uses PostgreSQL for data storage.

## Prerequisites

- Python 3.6+
- PostgreSQL server installed and running
- GitHub OAuth App credentials

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure PostgreSQL

- Make sure PostgreSQL is installed and running
- Edit the database configuration in `config.py` with your PostgreSQL credentials:
  - `DB_HOST`: PostgreSQL server host (default: localhost)
  - `DB_PORT`: PostgreSQL server port (default: 5432)
  - `DB_NAME`: Database name (default: github_tokens)
  - `DB_USER`: PostgreSQL username
  - `DB_PASSWORD`: PostgreSQL password

### 3. Initialize the Database

Run the database initialization script:

```bash
python init_database.py
```

This will create the necessary database and tables.

### 4. Run the Application

```bash
python app.py
```

The application will be available at http://localhost:5000

## Features

- GitHub OAuth authentication
- View and download GitHub repositories
- Token management with automatic expiration
- Admin interface to view stored tokens

## Database Migration

This application has been migrated from SQLite to PostgreSQL for improved performance, reliability, and scalability.