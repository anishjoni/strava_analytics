"""Configuration management for Strava Analytics pipeline."""

import os
from pathlib import Path
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # Strava API Configuration
    strava_client_id: Optional[str] = Field(default=None, env="STRAVA_CLIENT_ID")
    strava_client_secret: Optional[str] = Field(default=None, env="STRAVA_CLIENT_SECRET")
    
    # Database Configuration
    db_host: str = Field(default="localhost", env="DB_HOST")
    db_port: int = Field(default=3306, env="DB_PORT")
    db_name: str = Field(default="strava_db", env="DB_NAME")
    db_user: str = Field(default="strava_db_user", env="DB_USER")
    db_password: str = Field(default="StravaConnect", env="DB_PASSWORD")
    
    # File Paths
    tokens_file: str = Field(default="data/tokens.json", env="TOKENS_FILE")
    data_dir: str = Field(default="data", env="DATA_DIR")
    
    # Token Management
    token_refresh_buffer_minutes: int = Field(default=10, env="TOKEN_REFRESH_BUFFER_MINUTES")
    
    # Strava API Configuration
    strava_activities_per_page: int = Field(default=100, env="STRAVA_ACTIVITIES_PER_PAGE")
    strava_api_base_url: str = Field(default="https://www.strava.com/api/v3", env="STRAVA_API_BASE_URL")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # Ignore extra environment variables
    
    @property
    def database_url(self) -> str:
        """Get the database connection URL."""
        return f"mysql+mysqlconnector://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
    
    def ensure_data_dir(self) -> Path:
        """Ensure data directory exists and return Path object."""
        data_path = Path(self.data_dir)
        data_path.mkdir(exist_ok=True)
        return data_path
    
    @property
    def tokens_path(self) -> Path:
        """Get the full path to tokens file."""
        return self.ensure_data_dir() / "tokens.json"


# Global settings instance
settings = Settings()
