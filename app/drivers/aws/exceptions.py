class S3Exception(Exception):
    detail = "S3 Exception"

    def __init__(self, *args: str):
        super().__init__(self.detail)


class S3BucketNotFound(S3Exception):
    detail = "S3 Bucket not found"


class S3GetBucketsError(S3Exception):
    def __init__(self, status_code: int):
        self.detail = f"S3 Get Buckets Error: {status_code}"
        super().__init__(self.detail)


class S3BucketCreationError(S3Exception):
    def __init__(self, bucket: str, status_code: int):
        self.detail = f"S3 Bucket {bucket} creation fail with {status_code=}"
        super().__init__(self.detail)


class S3BucketAlreadyExists(S3Exception):
    def __init__(self, bucket: str):
        self.detail = f"S3 Bucket {bucket} already exists"
        super().__init__(self.detail)


class S3BucketNotEmpty(S3Exception):
    def __init__(self, bucket: str):
        self.detail = f"S3 Bucket {bucket} not empty! And cannot be deleted"
        super().__init__(self.detail)


class S3ListBucketsError(S3Exception):
    def __init__(self, status_code: int):
        self.detail = f"S3 List Buckets Error: {status_code}"
        super().__init__(self.detail)


class S3BucketDeletionError(S3Exception):
    def __init__(self, bucket: str, status_code: int):
        self.detail = f"S3 Bucket {bucket} deletion fail with {status_code=}"
        super().__init__(self.detail)


class S3BucketHeadError(S3Exception):
    def __init__(self, bucket: str, status_code: int):
        self.detail = f"S3 Bucket {bucket} head fail with {status_code=}"
        super().__init__(self.detail)


class S3ObjectsError(S3Exception):
    pass


class S3ListObjectsError(S3ObjectsError):
    def __init__(self, status_code: int):
        self.detail = f"S3 List Objects Error: {status_code}"
        super().__init__(self.detail)


class S3GetObjectError(S3ObjectsError):
    def __init__(self, status_code: int):
        self.detail = f"S3 Get Object Error: {status_code}"
        super().__init__(self.detail)


class S3DeleteObjectError(S3ObjectsError):
    def __init__(self, status_code: int):
        self.detail = f"S3 Delete Object Error: {status_code}"
        super().__init__(self.detail)


class S3ObjectCreationError(S3ObjectsError):
    def __init__(self, object_name: str, status_code: int):
        self.detail = f"S3 Object {object_name} creation fail with {status_code=}"
        super().__init__(self.detail)
