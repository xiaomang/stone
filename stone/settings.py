from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    应用配置类。
    """

    debug: bool = True
    mongo_uri: str = "mongodb://root:root.12*3@localhost:27017/stone?authSource=admin"
    mongo_name: str = "stone"

    model_config: SettingsConfigDict = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )
