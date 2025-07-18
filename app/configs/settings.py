from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class AwsSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix='AWS_')

    access_key: str
    secret_key: str
    region: str
    bucket_name: str
    endpoint_url: str
    session_token: str | None = None
