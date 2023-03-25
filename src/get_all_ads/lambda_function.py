import simplejson as json
import os
import boto3
from boto3.dynamodb.types import TypeDeserializer

client = boto3.client("dynamodb")


def ads_iter(deserializer, ads):
    for ad in ads.get("Items"):
        ad_parsed = {k: deserializer.deserialize(v) for k, v in ad.items()}
        yield ad_parsed


def lambda_handler(event, context):
    ads_table = os.environ.get("ADS_TABLE", None)
    if not ads_table:
        return {"statusCode": 500, "body": "Ads table not found"}

    # To go from low-level format to python
    deserializer = TypeDeserializer()

    ads = client.scan(TableName=ads_table)

    list_of_ads = list(ads_iter(deserializer, ads))
    return {"statusCode": 200, "body": json.dumps(list_of_ads)}
