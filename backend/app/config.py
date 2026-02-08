import os
from dataclasses import dataclass


def _require_env(name: str) -> str:
    """Read an environment variable or raise with a clear message."""
    value = os.environ.get(name, "")
    if not value:
        raise ValueError(
            f"Required environment variable '{name}' is not set. "
            f"Check your .env file or environment configuration."
        )
    return value


@dataclass
class Settings:
    DATABASE_URL: str
    BETTER_AUTH_SECRET: str
    CORS_ORIGINS: str

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            DATABASE_URL=_require_env("DATABASE_URL"),
            BETTER_AUTH_SECRET=_require_env("BETTER_AUTH_SECRET"),
            CORS_ORIGINS=os.environ.get("CORS_ORIGINS", "http://localhost:3000"),
        )


settings = Settings.from_env()
