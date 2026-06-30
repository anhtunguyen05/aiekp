from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # API Settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # Neo4j Settings
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "password"

    # Qdrant Settings
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


settings = Settings()
