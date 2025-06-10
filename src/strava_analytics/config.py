"""Configuration management for Strava Analytics pipeline."""

from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings


def get_project_root() -> Path:
    """Get the project root directory."""
    # Start from this file's directory and go up to find the project root
    current_path = Path(__file__).parent
    while current_path != current_path.parent:
        if (current_path / "pyproject.toml").exists():
            return current_path
        current_path = current_path.parent

    # Fallback to current working directory
    return Path.cwd()


class Settings(BaseSettings):
    """Application settings."""

    # Strava API Configuration
    strava_client_id: Optional[str] = None
    strava_client_secret: Optional[str] = None

    # Database Configuration
    db_host: str = "localhost"
    db_port: int = 3306
    db_name: str = "strava_db"
    db_user: str = "strava_db_user"
    db_password: str = "StravaConnect"

    # File Paths (relative to project root)
    tokens_file: str = "tokens.json"
    data_dir: str = "data"

    # Token Management
    token_refresh_buffer_minutes: int = 10

    # Strava API Configuration
    strava_activities_per_page: int = 100
    strava_api_base_url: str = "https://www.strava.com/api/v3"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore"  # Ignore extra environment variables
    }

    @property
    def project_root(self) -> Path:
        """Get the project root directory."""
        return get_project_root()

    @property
    def database_url(self) -> str:
        """Get the database connection URL."""
        return f"mysql+mysqlconnector://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    @property
    def data_path(self) -> Path:
        """Get the absolute path to data directory."""
        return self.project_root / self.data_dir

    def ensure_data_dir(self) -> Path:
        """Ensure data directory exists and return Path object."""
        data_path = self.data_path
        data_path.mkdir(exist_ok=True)
        return data_path

    @property
    def tokens_path(self) -> Path:
        """Get the full path to tokens file."""
        if self.tokens_file == "tokens.json":
            # Store tokens.json in project root for backward compatibility
            return self.project_root / self.tokens_file
        else:
            # If custom path specified, use it relative to project root
            return self.project_root / self.tokens_file


# Global settings instance
settings = Settings()
