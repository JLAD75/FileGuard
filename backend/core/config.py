import os

# For now, we use a default local PostgreSQL instance.
# In a real-world scenario, this would come from environment variables.
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/file_management_db")

# This will be used by Alembic
POSTGRES_DB = os.getenv("POSTGRES_DB", "file_management_db")
POSTGRES_USER = os.getenv("POSTGRES_USER", "user")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "password")
POSTGRES_SERVER = os.getenv("POSTGRES_SERVER", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")

# Construct the database URL for SQLAlchemy and Alembic
DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"