# dynamodb.py

import boto3
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError
from logger import logger


class DynamoDB:
    """
    A Class for DynamoDB related API operations
    """

    def __init__(self, table_name):
        self.table_name = table_name
        self.table = boto3.resource('dynamodb').Table(table_name)

    def get_items_in_service(self, index_name, service):
        """
        Query on GSI to get all items for a specific ECS service
        """
        try:
            response = self.table.query(
                IndexName=index_name,
                FilterExpression=Attr('group').eq('service') &
                Attr('groupName').eq(service)
            )
            logger.debug('Query items: %s', response['Items'])
            return response['Items']
        except ClientError as e:
            logger.error('Failed to query table: %s', e)
            raise ClientError('Failed to query table: ', e)

    def get_services_names(self, index_name):
        """
        Scan on GSI to get all ECS service names in Table
        """
        try:
            response = self.table.scan(
                FilterExpression=Attr('group').eq('service')
            )
            logger.debug('Scanned ECS services: %s', response['Items'])
            return response['Items']
        except ClientError as e:
            logger.error('Failed to scan table: %s', e)
            raise ClientError('Failed to scan table: ', e)
