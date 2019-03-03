import boto3
import requests

from googmusic import app


class S3Manager(object):
    s3 = None
    bucket = None

    def __init__(self, bucket):
        self.bucket = bucket
        self.s3 = boto3.client(
            's3',
            aws_access_key_id=app.config['AWS_ACCESS_KEY_ID'],
            aws_secret_access_key=app.config['AWS_SECRET_ACCESS_KEY']
        )

    def ensure_file_exists(self, key, source_url=None):
        if not self._exists(key):
            if source_url is not None:
                data = self._get_stream_from_url(source_url)
                self.s3.upload_fileobj(data, self.bucket, key)
        return self.url(key)

    def url(self, key):
        return self.s3.generate_presigned_url(
            'get_object',
            Params={ 'Bucket': self.bucket, 'Key': key },
            ExpiresIn=43200
        )

    def _exists(self, key):
        bucket_data = self.s3.list_objects(Bucket=self.bucket)
        if 'Contents' not in bucket_data.keys():
            return False

        all_files = [file['Key'] for file in self.s3.list_objects(Bucket=self.bucket)['Contents']]
        if key in all_files:
            return True

        return False

    def _get_stream_from_url(self, url):
        stream = requests.get(url, stream=True)
        return stream.raw
