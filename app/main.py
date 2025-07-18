import argparse
from datetime import datetime
from pathlib import Path

from alive_progress import alive_bar
from pydantic import BaseModel

from app.configs.settings import AwsSettings
from app.drivers.aws.buckets import S3Bucket, S3BucketAlreadyExists, S3Client, S3Object


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", "-d", type=str, required=True)
    return parser.parse_args()


class ReadableObject(BaseModel):
    key: str
    size: int
    last_modified: datetime

    @classmethod
    def convert(cls, bucket_objects: list[BaseModel]) -> tuple[BaseModel, ...]:
        return tuple(
            map(
                lambda x: cls(key=x.key, size=x.size, last_modified=x.last_modified),
                bucket_objects,
            )
        )


def main():
    args = parse_args()
    OUTPUT_DIR = Path(args.output_dir)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    aws_settings = AwsSettings()
    print(aws_settings)

    s3_client = S3Client(aws_settings)
    s3_bucket = S3Bucket(s3_client, aws_settings.bucket_name)
    try:
        s3_bucket.create()
    except S3BucketAlreadyExists:
        pass

    # objects = ReadableObject.convert(s3_bucket.list_objects())
    objects = s3_bucket.list_objects()
    size_objects = len(objects)

    with alive_bar(size_objects, title="Downloading files") as bar:
        for obj in objects:
            object_path = Path(obj.key)
            print(f"Save file in path: {object_path}; Size: {obj.size};")
            s3_object = S3Object(s3_bucket, str(object_path))
            body_obj = s3_object.get()

            object_path = OUTPUT_DIR / object_path
            object_path.parent.mkdir(parents=True, exist_ok=True)
            with open(object_path, "wb") as f:
                f.write(body_obj.read())
            bar()


if __name__ == "__main__":
    main()
