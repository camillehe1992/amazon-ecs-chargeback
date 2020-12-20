# s3.py

import boto3
from botocore.exceptions import ClientError
from logger import logger


class S3:
    """
    A Class for S3 related API operation
    """

    def __init__(self, bucket):
        self.bucket = bucket
        self.client = boto3.client('s3')

    def put_object(self, body, key):
        """
        Add an objecct to a bucket
        """
        try:
            response = self.client.put_object(
                Body=body,
                Bucket=self.bucket,
                Key=key
            )
            logger.debug('Put object: %s', response)
            return response
        except ClientError as e:
            logger.error('Failed to put objecct: %s', e)
            raise ClientError('Failed to put objecct: ', e)
