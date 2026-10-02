""" Configuration for the application (Let the python know the address and password for the database)"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str | None = Field(default=None, validation_alias="DATABASE_URL")

    postgres_db: str = Field(default="gradatlas", validation_alias="POSTGRES_DB")
    postgres_user: str = Field(default="gradatlas", validation_alias="POSTGRES_USER")
    postgres_password: str = Field(default="", validation_alias="POSTGRES_PASSWORD")
    postgres_host: str = Field(default="db", validation_alias="POSTGRES_HOST")
    postgres_port: int = Field(default=5432, validation_alias="POSTGRES_PORT")

    embedding_dimensions: int = 1536
    snapshot_dir: str = Field(default="/app/data/snapshots", validation_alias="SNAPSHOT_DIR")

    deepseek_api_key: str = Field(default="", validation_alias="DEEPSEEK_API_KEY")
    deepseek_base_url: str = Field(
        default="https://api.deepseek.com", validation_alias="DEEPSEEK_BASE_URL"
    )
    chat_model: str = Field(default="deepseek-flash", validation_alias="CHAT_MODEL")

    embedding_api_key: str = Field(default="", validation_alias="EMBEDDING_API_KEY")
    embedding_base_url: str = Field(
        default="https://api.openai.com/v1", validation_alias="EMBEDDING_BASE_URL"
    )
    embedding_model: str = Field(
        default="text-embedding-3-small", validation_alias="EMBEDDING_MODEL"
    )

    google_client_id: str = Field(default="", validation_alias="GOOGLE_CLIENT_ID")
    google_client_secret: str = Field(default="", validation_alias="GOOGLE_CLIENT_SECRET")
    google_redirect_uri: str = Field(default="", validation_alias="GOOGLE_REDIRECT_URI")

    @property
    def db_url(self) -> str:
        if self.database_url:
            return self.database_url
        return (
            f"postgresql+psycopg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

settings = Settings()