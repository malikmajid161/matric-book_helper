from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=Path(__file__).parent / '.env', extra='ignore')
    gemini_api_key: str = ''
    gemini_model: str = 'gemini-3.5-flash-lite'
    cors_origins: str = 'http://localhost:3000,http://127.0.0.1:3000'
    data_dir: Path = Path(__file__).parent / 'data'
    study_access_code: str = ''
    max_distance: float = 0.65
    retrieval_mode: str = 'lexical'
    student_profiles_json: str = ''


settings = Settings()
