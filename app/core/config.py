# Standard library imports
import os
from pathlib import Path

# Third-party imports
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import dotenv_values, find_dotenv


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables, .env file, or defaults.
    
    Priority order:
    1. OS environment variables (highest)
    2. .env file
    3. Default values (lowest)
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"  # Ignore extra env vars not in model
    )
    
    # Application version
    VERSION: str = "0.1.0"
    
    # Application configuration
    ENVIRONMENT: str = "development"
    DEBUG: str = "false"
    PUBLISH_PORT: int = 8000
    
    # MongoDB configuration
    MONGO_USER: str = "root"
    MONGO_PASS: str = "pass"
    MONGO_HOST: str = "mongodb"
    MONGO_PORT: str = "27017"
    MONGO_AUTH_SOURCE: str = "admin"
    MONGO_DATABASE: str = "fastapi_starter"


# Initialize settings instance
settings = Settings()


# For backward compatibility, expose settings as module-level variables
VERSION: str = settings.VERSION
ENVIRONMENT: str = settings.ENVIRONMENT
DEBUG: bool = settings.DEBUG.lower() == "true"
PUBLISH_PORT: int = settings.PUBLISH_PORT

# MongoDB configuration
MONGO_USER: str = settings.MONGO_USER
MONGO_PASS: str = settings.MONGO_PASS
MONGO_HOST: str = settings.MONGO_HOST
MONGO_PORT: str = settings.MONGO_PORT
MONGO_AUTH_SOURCE: str = settings.MONGO_AUTH_SOURCE
MONGO_DATABASE: str = settings.MONGO_DATABASE

# MongoDB connection string (computed from settings)
MONGO_URI: str = f"mongodb://{MONGO_USER}:{MONGO_PASS}@{MONGO_HOST}:{MONGO_PORT}/{MONGO_DATABASE}?authSource={MONGO_AUTH_SOURCE}"


def print_config_values() -> None:
    """
    Print all configuration values for debugging purposes.
    Shows the source of each value: OS (environment variable), .env (file), or default.
    This function should only be called during development or troubleshooting.
    """
    # Load .env file data if it exists
    env_file_path = Path(".env")
    env_file_data = {}
    if env_file_path.exists():
        env_file_data = dotenv_values(env_file_path)
    else:
        # Try to find .env file using dotenv's find_dotenv
        dotenv_path = find_dotenv()
        if dotenv_path:
            env_file_data = dotenv_values(dotenv_path)
    
    os_env = os.environ
    
    print("\n=== Configuration Values (with sources) ===")
    for field_name, field in settings.model_fields.items():
        value = getattr(settings, field_name)
        
        # Determine source
        env_key = field_name  # Pydantic uses field name as env var name by default
        if env_key in os_env:
            source = "[OS]"
        elif env_key in env_file_data:
            source = "[.env]"
        else:
            source = "[default]"
        
        # Mask sensitive values
        if "PASS" in field_name or "PASSWORD" in field_name:
            display_value = "***" if value else "None"
        else:
            display_value = repr(value) if value is not None else "None"
        
        print(f"             {field_name}: {display_value} {source}")
    
    # Print computed values
    print(f"\n             MONGO_URI: mongodb://{MONGO_USER}:***@{MONGO_HOST}:{MONGO_PORT}/{MONGO_DATABASE}?authSource={MONGO_AUTH_SOURCE} [computed]")
    print(f"             DEBUG (bool): {DEBUG} [computed]")
    
    if DEBUG:
        print("\n=== Debug Information ===")
        print(f"Working Directory: {os.getcwd()}")
        print(f"PYTHONPATH: {os.getenv('PYTHONPATH', 'Not set')}")
        dotenv_path = find_dotenv() if not env_file_path.exists() else str(env_file_path)
        print(f"ENV File: {dotenv_path if dotenv_path else 'Not found'}")
    
    print("===========================================\n")


# Print configuration values on module load
print_config_values()
