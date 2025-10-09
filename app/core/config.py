# Standard library imports
import os
from typing import Optional, Any

# Third-party imports
from dotenv import load_dotenv, find_dotenv

def get_env_variable(name: str, default: Optional[str] = None, required: bool = True) -> Optional[str]:
    """
    Get an environment variable with a default value.

    Args:
        name (str): The name of the environment variable
        default (Optional[str]): Default value if the variable is not set
        required (bool): Whether the variable is required. If True and not set, raises EnvironmentError

    Returns:
        Optional[str]: The value of the environment variable or the default value

    Raises:
        EnvironmentError: If the variable is required but not set
    """
    value = os.getenv(name, default)
    if required and value is None:
        raise EnvironmentError(f"Required environment variable '{name}' is not set.")
    return value

def print_config_values() -> None:
    """
    Print all configuration values for debugging purposes.
    This function should only be called during development or troubleshooting.
    """
    print("\n=== Application Configuration ===")
    print(f"VERSION: {VERSION}")
    print(f"ENVIRONMENT: {ENVIRONMENT}")
    print(f"DEBUG: {DEBUG}")
    print(f"PUBLISH_PORT: {PUBLISH_PORT}")
    
    print("\n=== MongoDB Configuration ===")
    print(f"MONGO_HOST: {MONGO_HOST}")
    print(f"MONGO_PORT: {MONGO_PORT}")
    print(f"MONGO_USER: {MONGO_USER}")
    print(f"MONGO_AUTH_SOURCE: {MONGO_AUTH_SOURCE}")
    print(f"MONGO_DATABASE: {MONGO_DATABASE}")
    print(f"MONGO_URI: mongodb://{MONGO_USER}:***@{MONGO_HOST}:{MONGO_PORT}/{MONGO_DATABASE}?authSource={MONGO_AUTH_SOURCE}")
    
    if DEBUG:
        print("\n=== Debug Information ===")
        print(f"Working Directory: {os.getcwd()}")
        print(f"PYTHONPATH: {os.getenv('PYTHONPATH', 'Not set')}")
        print(f"ENV File: {dotenv_path if dotenv_path else 'Not found'}")

# Load environment variables
dotenv_path = find_dotenv()
if not dotenv_path:
    print("   WARNING   ENV FILE: not found")
    print("      INFO   ENV VARIABLES: will be loaded from the system")
    print("   WARNING   ENV VARIABLES not already set: will use DEFAULT values where applicable")
else:
    # Load environment variables from the .env file
    load_dotenv(dotenv_path)

# Application configuration
VERSION: str = get_env_variable("VERSION", default="0.1.0", required=False)
ENVIRONMENT: str = get_env_variable("ENVIRONMENT", default="development", required=False)
DEBUG: bool = get_env_variable("DEBUG", default="false", required=False).lower() == "true"
PUBLISH_PORT: int = int(get_env_variable("PUBLISH_PORT", default="8000", required=False))

# MongoDB configuration
MONGO_USER: str = get_env_variable("MONGO_USER", default="root")
MONGO_PASS: str = get_env_variable("MONGO_PASS", default="pass")
MONGO_HOST: str = get_env_variable("MONGO_HOST", default="mongodb")
MONGO_PORT: str = get_env_variable("MONGO_PORT", default="27017")
MONGO_AUTH_SOURCE: str = get_env_variable("MONGO_AUTH_SOURCE", default="admin")
MONGO_DATABASE: str = get_env_variable("MONGO_DATABASE", default="fastapi_starter")

# MongoDB connection string (for debugging)
MONGO_URI: str = f"mongodb://{MONGO_USER}:{MONGO_PASS}@{MONGO_HOST}:{MONGO_PORT}/{MONGO_DATABASE}?authSource={MONGO_AUTH_SOURCE}"

# Print configuration values for debugging
print_config_values()