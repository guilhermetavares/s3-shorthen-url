import uuid
import boto3
import logging
import tempfile
import json

from botocore.exceptions import ClientError


logger = logging.getLogger(__name__)


class ShorthenUrl:

    def __init__(self, aws_access_key_id, aws_secret_access_key, aws_bucket, aws_shorthen_app):
        self.client = boto3.client(
            "s3",
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
        )
        self.bucket = aws_bucket
        self.aws_shorthen_app = aws_shorthen_app

    def get_filename(self):
        filename = uuid.uuid4().hex[:16]

        try:
            self.client.head_object(Bucket=self.bucket, Key=filename)
        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                return filename

        return self.get_filename()  # pragma: no cover

    def shorten_url(self, url, filename=None):

        filename = self.get_filename()

        content = {
            "file_name": filename,
            "url": url,
            "app": self.aws_shorthen_app,
        }

        logger.info("ShorthenUrl", extra=content)

        temp_file = tempfile.TemporaryFile()
        temp_file.write(json.dumps(content).encode())
        temp_file.seek(0)

        self.client.upload_fileobj(
            temp_file,
            self.bucket,
            filename,
            ExtraArgs={"WebsiteRedirectLocation": url},
        )

        temp_file.close()

        return f"https://{self.bucket}/{filename}"
