from typing import Optional, Protocol

from boto3 import Session


class S3Config(Protocol):
    __slots__ = ()
    endpoint_url: str = "http://127.0.0.1:9000"
    access_key: str
    secret_key: str
    session_token: Optional[str] = None


class S3Client:
    def __init__(
        self,
        config: S3Config,
    ):
        self.session = Session()
        self.s3_client = self.session.client(
            service_name="s3",
            aws_access_key_id=config.access_key,
            aws_secret_access_key=config.secret_key,
            aws_session_token=config.session_token,
            endpoint_url=config.endpoint_url,
        )
