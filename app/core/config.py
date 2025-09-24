import os
from dotenv import load_dotenv

load_dotenv()

def get_connection_string() -> str:
    engine = os.getenv("DB_ENGINE")
    username = os.getenv("DB_USERNAME")
    password = os.getenv("DB_PASSWORD")
    dbhost = os.getenv("DB_HOST")
    dbport = os.getenv("DB_PORT")
    dbname = os.getenv("DB_NAME")
    return f"{engine}://{username}:{password}@{dbhost}:{dbport}/{dbname}"

# Database connection string
SQLALCHEMY_DATABASE_URL = get_connection_string()

# JWT settings
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))