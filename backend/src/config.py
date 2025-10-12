import dotenv
import os

dotenv.load_dotenv()

def get_env_var(name: str, required: bool = True, default = None):
    value = os.getenv(name, default)
    if required and (value is None or value.strip() == ""):
        raise EnvironmentError(f"Needed environment variable '{name}' is not defined.")
    return value

DB_PATH = get_env_var("DATABASE_URL")
KOMMO_DOMAIN = get_env_var("KOMMO_DOMAIN")
KOMMO_KEY = get_env_var("KOMMO_KEY")
CONVERT_PIPE = get_env_var("CONVERT_PIPELINE")
PLAN_PIPE = get_env_var("PLAN_PIPELINE")
WON_STATUS = get_env_var("WON_STATUS")
REDIS_HOST = get_env_var("REDIS_HOST")
REDIS_PORT = get_env_var("REDIS_PORT")
REDIS_DB = get_env_var("REDIS_DB")
CACHE_DURATION = get_env_var("CACHE_DURATION")
FOLLOW_PIPE = get_env_var("FOLLOW_PIPE")