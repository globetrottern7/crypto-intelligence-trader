from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    database_url: str = "postgresql+psycopg://crypto_app:change_me_local_only@localhost:5432/crypto_intelligence"
    backend_cors_origins: str = "http://localhost:3000"
    api_access_token: str = ""
    paper_initial_capital: float = 5000
    paper_fee_bps: float = 10
    paper_slippage_bps: float = 10
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origins(self) -> list[str]:
        return [x.strip() for x in self.backend_cors_origins.split(",") if x.strip()]


settings = Settings()
