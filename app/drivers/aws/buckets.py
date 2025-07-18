import logging
from typing import BinaryIO

# from botocore.errorfactory import BucketAlreadyOwnedByYou
from botocore.exceptions import ClientError

from .base import S3Client
from .exceptions import *
from .models import (
    Bucket,
    Content,
    Objects,
    ResponseCreateBucket,
    ResponseDeleteBucket,
    ResponseDeletedObjects,
    ResponseGetObject,
    ResponseHead,
    ResponseListBuckets,
    ResponseListObjectsBucket,
)

logger = logging.getLogger("app.drivers.aws.buckets")


class S3Bucket:
    def __init__(self, client: S3Client, bucket_name: str):
        self.s3_client = client.s3_client
        self.bucket_name = bucket_name

    def create(self) -> bool:
        try:
            response = ResponseCreateBucket(
                **self.s3_client.create_bucket(Bucket=self.bucket_name)
            )
            if response.metadata.http_status_code != 200:
                logger.error(
                    f"S3 Creation Bucket Error: {response.metadata.http_headers}"
                )
                raise S3BucketCreationError(
                    self.bucket_name, response.metadata.http_status_code
                )
        except ClientError as e:
            if e.response["Error"]["Code"] == "BucketAlreadyOwnedByYou":
                logger.warning(f"Bucket {self.bucket_name} already exists")
                raise S3BucketAlreadyExists(self.bucket_name)
            if e.response["Error"]["Code"] == "BucketNotEmpty":
                logger.warning(f"Bucket {self.bucket_name} already exists")
                raise S3BucketAlreadyExists(self.bucket_name)
            else:
                raise e
        return True

    def head(self) -> bool:
        response = ResponseHead(**self.s3_client.head_bucket(Bucket=self.bucket_name))
        if response.metadata.http_status_code != 200:
            logger.error(f"S3 Head Bucket Error: {response.metadata.http_headers}")
            raise S3BucketHeadError(
                self.bucket_name, response.metadata.http_status_code
            )
        return response

    def list_objects(self) -> list[Content]:
        response = ResponseListObjectsBucket(
            **self.s3_client.list_objects_v2(Bucket=self.bucket_name)
        )
        if response.metadata.http_status_code != 200:
            logger.error(f"S3 List Objects Error: {response.metadata.http_headers}")
            raise S3ListObjectsError(response.metadata.http_status_code)
        return response.contents

    def list(self) -> list[Bucket]:
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3/client/list_buckets.html#S3.Client.list_buckets
        response = ResponseListBuckets(**self.s3_client.list_buckets())
        # response = self._get_response_metadata(raw_response)
        if response.metadata.http_status_code != 200:
            logger.error(f"S3 List Buckets Error: {response.metadata.http_headers}")
            raise S3ListBucketsError(response.metadata.http_status_code)
        return response.buckets

    def delete(self) -> bool:
        response = ResponseDeleteBucket(
            **self.s3_client.delete_bucket(Bucket=self.bucket_name)
        )
        if response.metadata.http_status_code != 204:
            logger.error(f"S3 Delete Bucket Error: {response.metadata.http_headers}")
            raise S3BucketDeletionError(
                self.bucket_name, response.metadata.http_status_code
            )
        return True

    def prune(self) -> ResponseDeletedObjects:
        objects = Objects(Objects=self.list_objects())
        return ResponseDeletedObjects(
            **self.s3_client.delete_objects(
                Bucket=self.bucket_name, Delete=objects.model_dump()
            )
        )


class S3Object:
    def __init__(self, bucket: S3Bucket, object_name: str):
        self.s3_client = bucket.s3_client
        self.bucket_name = bucket.bucket_name
        self.object_name = object_name

    def upload(self, full_path_to_file: str) -> None:
        self.s3_client.upload_file(
            full_path_to_file, self.bucket_name, self.object_name
        )

    def binary_upload(self, file: BinaryIO) -> None:
        self.s3_client.upload_fileobj(file, self.bucket_name, self.object_name)

    def get(self) -> BinaryIO:
        response = ResponseGetObject(
            **self.s3_client.get_object(Bucket=self.bucket_name, Key=self.object_name)
        )
        if response.metadata.http_status_code != 200:
            logger.error(f"S3 List Buckets Error: {response.metadata.http_headers}")
            raise S3GetObjectError(response.metadata.http_status_code)
        return response.body

    def list(self) -> list[Content]:
        response = ResponseListObjectsBucket(
            **self.s3_client.list_objects(Bucket=self.bucket_name)
        )
        if response.metadata.http_status_code != 200:
            logger.error(f"S3 List Buckets Error: {response.metadata.http_headers}")
            raise S3ListObjectsError(response.metadata.http_status_code)
        return response.contents

    def delete(self) -> bool:
        response = ResponseDeleteBucket(
            **self.s3_client.delete_object(
                Bucket=self.bucket_name, Key=self.object_name
            )
        )
        if response.metadata.http_status_code != 204:
            logger.error(f"S3 Delete Object Error: {response.metadata.http_headers}")
            raise S3DeleteObjectError(response.metadata.http_status_code)
        return True


class S3Objects:
    def __init__(self, bucket: S3Bucket):
        self.s3_client = bucket.s3_client
        self.bucket_name = bucket.bucket_name

    def delete(self, objects: Objects):
        return self.s3_client.delete_objects(
            Bucket=self.bucket_name, Delete=objects.model_dump()
        )
