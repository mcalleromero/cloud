import json
import time
import boto3
import os

client = boto3.client("dynamodb")


def lambda_handler(event, context):
    currtime = int(time.time())
    ad_id = event["ad_id"]
    timestamp = ad_id.split("_")[0]

    ads_table = os.environ.get("ADS_TABLE", None)
    if not ads_table:
        return {"statusCode": 500, "body": "Ads table not found"}

    comments_table = os.environ.get("COMMENTS_TABLE", None)
    if not comments_table:
        return {"statusCode": 500, "body": "Comments table not found"}

    ad = client.get_item(
        TableName=ads_table, Key={"id": {"S": ad_id}, "timestamp": {"N": timestamp}}
    )
    if not ad.get("Item"):
        return {"statusCode": 404, "body": json.dumps("Item not found")}

    client.put_item(
        TableName=comments_table,
        Item={
            "ad_id": {"S": event["ad_id"]},
            "timestamp": {"N": str(currtime)},
            "user": {"S": event["user"]},
            "comment": {"S": event["comment"]},
        },
    )
    return {"statusCode": 200}
