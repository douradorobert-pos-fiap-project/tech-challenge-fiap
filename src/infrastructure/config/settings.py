from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Sistema de Oficina"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"

    DATABASE_URL: str = "sqlite:///./data/oficina.db"
    CPF_VALIDATOR_LAMBDA_ARN: str = ""
    AWS_REGION: str = "us-east-1"

    JWT_SECRET: str = "dev-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 60

    SMTP_HOST: str = "localhost"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = "noreply@oficina.com"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
