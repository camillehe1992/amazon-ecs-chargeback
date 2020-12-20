# pricing.py

import boto3
from botocore.exceptions import ClientError
import ast
import re
from logger import logger


class Pricing:
    """
    A Class for Pricing related API operation
    """

    def __init__(self, srv_code):
        self.srv_code = srv_code
        self.client = boto3.client('pricing', region_name='us-east-1')

    def ec2_pricing(self, region, instance_type, tenancy, ostype):
        """
        Query AWS Pricing APIs to find cost of EC2 instance in the region.
        Given the paramters we use at input, we should get a UNIQUE result.
        TODO: In the current version, we only consider OnDemand price. If
        we start considering actual cost, we need to consider input from
        CUR on an hourly basis.
        """
        try:
            response = self.client.get_products(
                ServiceCode=self.srv_code,
                Filter=[
                    {'Type': 'TERM_MATCH', 'Field': 'location',
                        'Value': region},
                    {'Type': 'TERM_MATCH', 'Field': 'servicecode',
                        'Value': self.srv_code},
                    {'Type': 'TERM_MATCH', 'Field': 'preInstalledSw',   'Value': 'NA'},
                    {'Type': 'TERM_MATCH', 'Field': 'tenancy',
                        'Value': tenancy},
                    {'Type': 'TERM_MATCH', 'Field': 'instanceType',
                        'Value': instance_type},
                    {'Type': 'TERM_MATCH', 'Field': 'operatingSystem',  'Value': ostype}
                ],
                MaxResults=100
            )
            logger.info('Get Pricing products: %s', response)
            return self.parse_ec2_pricing(response)
        except ClientError as e:
            logger.error('Failed to get EC2 price: %s', e)
            raise ClientError('Failed to EC2 price: ', e)

    def parse_ec2_pricing(self, response):
        """
        Extract EC2 CPU and Memory price
        """
        try:
            ret_list = []
            if 'PriceList' in response:
                for iter in response['PriceList']:
                    ret_dict = {}
                    pricing_dict = ast.literal_eval(iter)
                    ret_dict['memory'] = pricing_dict['product']['attributes']['memory']
                    ret_dict['vcpu'] = pricing_dict['product']['attributes']['vcpu']
                    ret_dict['instanceType'] = pricing_dict['product']['attributes']['instanceType']
                    ret_dict['operatingSystem'] = pricing_dict['product']['attributes']['operatingSystem']
                    ret_dict['normalizationSizeFactor'] = pricing_dict['product']['attributes']['normalizationSizeFactor']

                    pricing_dict_terms = pricing_dict['terms']['OnDemand'][list(
                        pricing_dict['terms']['OnDemand'].keys())[0]]
                    ret_dict['unit'] = pricing_dict_terms['priceDimensions'][list(
                        pricing_dict_terms['priceDimensions'].keys())[0]]['unit']
                    ret_dict['pricePerUnit'] = pricing_dict_terms['priceDimensions'][list(
                        pricing_dict_terms['priceDimensions'].keys())[0]]['pricePerUnit']
                    ret_list.append(ret_dict)

            ec2_cpu = float(ret_list[0]['vcpu'])
            ec2_mem = float(re.findall(
                r"[+-]?\d+\.?\d*", ret_list[0]['memory'])[0])
            ec2_cost = float(ret_list[0]['pricePerUnit']['USD'])
            logger.debug(
                'Parsed EC2 price: ec2_cpu - %s, ec2_mem - %s, ec2_cost - %s', ec2_cpu, ec2_mem, ec2_cost)
            return (ec2_cpu, ec2_mem, ec2_cost)
        except Exception as e:
            logger.error('Failed to parse price: %s', e)
            raise ClientError('Failed to parse price: ', e)
