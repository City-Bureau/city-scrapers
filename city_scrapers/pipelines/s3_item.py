import os
import json
import boto3
from botocore.exceptions import ClientError
from datetime import datetime

from scrapy.utils.project import get_project_settings

s3_client = boto3.client('s3')
settings = get_project_settings()


class CityScrapersS3ItemPipeline(object):
    """
    Pipeline for writing each individual meeting to an S3 bucket
    with its ID as the key. Checks if the key exists, and only
    updates it if it does if the contents have changed
    """
    def process_item(self, item, spider):
        item_obj = item.copy()
        for k, v in item_obj.items():
            if isinstance(v, datetime):
                item_obj[k] = v.strftime('%Y-%m-%dT%H:%M:%S')
        bucket = settings.get('S3_ITEM_BUCKET')
        item_key = item_obj['id'] + '.json'

        put_s3_item = None
        try:
            s3_item_obj = s3_client.get_object(Bucket=bucket, Key=item_key)
            s3_item_obj = json.loads(s3_item_obj['Body'].read().decode('utf-8'))
            if item_obj != s3_item_obj:
                put_s3_item = item_obj
        except ClientError:
            put_s3_item = item_obj

        if put_s3_item is None:
            return item

        s3_client.put_object(
            Bucket=settings.get('S3_ITEM_BUCKET'),
            Key=item_obj['id'] + '.json',
            Body=json.dumps(put_s3_item).encode(),
        )
        return item
