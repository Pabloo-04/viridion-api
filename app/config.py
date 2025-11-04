from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    """Application settings"""
    
    # Database
    database_url: str
    
    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = False
    
    # CORS
    cors_origins: str = "http://localhost:5173"
    
    # ML Model
    model_path: str = "app/models/trained_model.pkl"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False
    )
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Convert comma-separated CORS origins to list"""
        return [origin.strip() for origin in self.cors_origins.split(",")]


settings = Settings()