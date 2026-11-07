"""应用配置。所有配置均可通过环境变量或 backend/.env 覆盖。"""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ---- App ----
    PROJECT_NAME: str = "SmartCMS"
    API_V1_PREFIX: str = "/api/v1"

    # ---- Database ----
    DATABASE_URL: str = "sqlite:///./smartcms.db"

    # ---- Auth ----
    SECRET_KEY: str = "change-me-to-a-random-secret-key-at-least-32-bytes-long"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    # ---- CORS ----
    CORS_ORIGINS: str = "http://localhost:5173"

    # ---- Storage ----
    STORAGE_DIR: str = "../storage"
    MAX_UPLOAD_SIZE_MB: int = 20

    # ---- 管理员初始化 ----
    ADMIN_USERNAME: str = "admin"
    ADMIN_EMAIL: str = "admin@example.com"
    ADMIN_PASSWORD: str = "admin123"

    # ---- LLM (DeepSeek) ----
    LLM_PROVIDER: str = "deepseek"  # deepseek | fake
    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com"
    DEEPSEEK_MODEL: str = "deepseek-chat"

    # ---- Embedding ----
    EMBEDDING_PROVIDER: str = "cloud"  # cloud | fake
    EMBEDDING_API_KEY: str = ""
    EMBEDDING_BASE_URL: str = "https://api.siliconflow.cn/v1"
    EMBEDDING_MODEL: str = "BAAI/bge-m3"
    EMBEDDING_DIM: int = 1024
    EMBEDDING_BATCH_SIZE: int = 16

    # ---- RAG ----
    CHUNK_SIZE: int = 500          # 分块大小（tokens）
    CHUNK_OVERLAP: int = 80        # 重叠（tokens）
    CHARS_PER_TOKEN: float = 4.0   # 字符/token 粗略估算，用于字符切分
    TOP_K: int = 5
    SIMILARITY_THRESHOLD: float = 0.3

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    @property
    def is_postgres(self) -> bool:
        return self.DATABASE_URL.startswith("postgresql")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
