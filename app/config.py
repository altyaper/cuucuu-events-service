from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://postgres:postgres@localhost:5432/cuucuu_dev"
    event_threshold: float = 0.65
    classifier_type: str = "rule_based"
    model_path: str = "./models/beto-events"
    batch_size: int = 100

    model_config = {"env_prefix": "EVENT_", "env_file": ".env"}


settings = Settings()
