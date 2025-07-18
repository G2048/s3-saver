from datetime import datetime
from typing import BinaryIO, TypeAlias

from botocore.httpchecksum import StreamingChecksumBody
from botocore.response import StreamingBody
from pydantic import AliasChoices, BaseModel, ConfigDict, Field

HTTPStatus: TypeAlias = int


class HTTPHeaders(BaseModel):
    content_length: str = Field(alias="content-length")
    content_type: str = Field(alias="content-type")
    server: str = Field(alias="server")
    strict_transport_security: str = Field(alias="strict-transport-security")
    vary: str = Field(alias="vary")
    x_amz_id_2: str = Field(alias="x-amz-id-2")
    x_amz_request_id: str = Field(alias="x-amz-request-id")
    x_content_type_options: str = Field(alias="x-content-type-options")
    x_ratelimit_limit: str = Field(alias="x-ratelimit-limit")
    x_ratelimit_remaining: str = Field(alias="x-ratelimit-remaining")
    x_xss_protection: str = Field(alias="x-xss-protection")
    date: str = Field(alias="date")


class ResponseMetadata(BaseModel):
    request_id: str = Field(alias="RequestId")
    host_id: str = Field(alias="HostId")
    http_status_code: HTTPStatus = Field(alias="HTTPStatusCode", default=200)
    http_headers: HTTPHeaders | dict[str, str] = Field(alias="HTTPHeaders")
    retry_attempts: int | None = Field(alias="RetryAttempts", default=0)
    checksum_algorithm: str | None = Field(alias="ChecksumAlgorithm", default=None)


class ResponseHead(BaseModel):
    metadata: ResponseMetadata = Field(alias="ResponseMetadata")


class ResponseCreateBucket(ResponseHead):
    location: str = Field(alias="Location")


class ResponseDeleteBucket(ResponseHead):
    pass


class Object(BaseModel):
    model_config = ConfigDict(extra="ignore")

    key: str = Field(alias="Key")

    def model_dump(self, *args, **kwargs):
        return super().model_dump(by_alias=True, *args, **kwargs)


class BinaryUploadFile(Object):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    file: BinaryIO


class Objects(BaseModel):
    model_config = ConfigDict(extra="ignore")

    objects: list[Object] = Field(alias="Objects")

    def model_dump(self, *args, **kwargs):
        return super().model_dump(by_alias=True, *args, **kwargs)


class Bucket(BaseModel):
    name: str = Field(alias="Name")
    creation_date: datetime = Field(alias="CreationDate")


class Owner(BaseModel):
    display_name: str = Field(alias="DisplayName")
    id: str = Field(alias="ID")


class ResponseListBuckets(ResponseHead):
    buckets: list[Bucket] = Field(alias="Buckets")
    owner: Owner = Field(alias="Owner")


class Content(Object):
    last_modified: datetime = Field(
        validation_alias=AliasChoices("last_modified", "LastModified")
    )
    etag: str = Field(validation_alias=AliasChoices("etag", "ETag"))
    size: int = Field(validation_alias=AliasChoices("size", "Size"))
    storage_class: str = Field(
        validation_alias=AliasChoices("storage_class", "StorageClass")
    )
    owner: Owner | None = Field(alias="Owner", default=None)


class Contents(BaseModel):
    model_config = ConfigDict(extra="ignore")

    contents: list[Content] = Field(alias="Contents")

    def model_dump(self, *args, **kwargs):
        return super().model_dump(by_alias=True, *args, **kwargs)


class ResponseGetObject(ResponseHead):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    accept_ranges: str = Field(alias="AcceptRanges")
    last_modified: datetime = Field(alias="LastModified")

    content_length: int = Field(alias="ContentLength")
    check_sum: str | None = Field(alias="ChecksumCRC32", default=None)
    content_type: str = Field(alias="ContentType")
    metadata_object: dict[str, str] = Field(alias="Metadata", default_factory=dict)
    body: StreamingChecksumBody | StreamingBody = Field(alias="Body")


# For list_objects v1 and v2
class ResponseListObjectsBucket(ResponseHead):
    is_truncated: bool | None = Field(alias="IsTruncated", default=None)  # v1
    marker: str | None = Field(alias="Marker", default="")  # v1

    contents: list[Content] = Field(alias="Contents")
    name: str = Field(alias="Name")
    prefix: str = Field(alias="Prefix")
    max_keys: int = Field(alias="MaxKeys")
    encoding_type: str = Field(alias="EncodingType")
    key_count: int | None = Field(alias="KeyCount", default=None)  # v2


class ResponseDeletedObjects(ResponseHead):
    deleted: list[Object] = Field(alias="Deleted")


class UploadFile(BaseModel):
    file_path: str
    key: str


class ListObjects(BaseModel):
    objects: list[Object] = Field(alias="Objects")


if __name__ == "__main__":
    # print(ResponseListObjectsBucket.model_json_schema())
    list_objects_result = [
        Content(
            key="test.txt",
            last_modified=datetime(2025, 6, 1, 9, 8, 13, 346000),
            etag='"ab5bb673a9b6c47be7125d85f3176af4"',
            size=785,
            storage_class="STANDARD",
        )
    ]
    print(list_objects_result)
    print()
    contents = Contents(Contents=list_objects_result)
    print(f"Contents: {contents}")
    print()
    objects = Objects(Objects=list_objects_result)
    print(f"Objects: {objects}")
    print()
    print(f"{objects.model_dump_json()}")
    print()
    # object = Object(**list_objects_result[0].model_dump())
    # print("Object: ", object)
    # print()
