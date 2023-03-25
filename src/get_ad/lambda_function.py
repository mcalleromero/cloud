import simplejson as json
import io
import os
import boto3
import base64
from boto3.dynamodb.types import TypeDeserializer


dynamo_client = boto3.client("dynamodb")
s3_client = boto3.client("s3")


def comments_iter(deserializer, comments):
    for comment in comments.get("Items"):
        comment_parsed = {k: deserializer.deserialize(v) for k, v in comment.items()}
        comment_parsed.pop("ad_id")
        yield comment_parsed


def find_bucket_key(image_path):
    splitted_image_path = image_path.split("/")
    return splitted_image_path[2], splitted_image_path[-1]


def lambda_handler(event, context):
    ad_id = event["ad_id"]
    timestamp = ad_id.split("_")[0]

    ads_table = os.environ.get("ADS_TABLE", None)
    if not ads_table:
        return {"statusCode": 500, "body": "Ads table not found"}

    comments_table = os.environ.get("COMMENTS_TABLE", None)
    if not comments_table:
        return {"statusCode": 500, "body": "Comments table not found"}

    # To go from low-level format to python
    deserializer = TypeDeserializer()

    response = {}

    ad = dynamo_client.get_item(
        TableName=ads_table, Key={"id": {"S": ad_id}, "timestamp": {"N": timestamp}}
    )

    if not ad.get("Item"):
        return {"statusCode": 404, "body": json.dumps("Item not found")}

    comments = dynamo_client.query(
        TableName=comments_table,
        KeyConditionExpression=f"ad_id = :ad_id",
        ExpressionAttributeValues={":ad_id": {"S": ad_id}},
    )

    comments_dict = {"comments": list(comments_iter(deserializer, comments))}

    ad = {k: deserializer.deserialize(v) for k, v in ad.get("Item").items()}

    response.update(**ad, **comments_dict)

    try:
        image_path = ad.pop("image_path")

        bucket, key = find_bucket_key(image_path)
        bytes_buffer = io.BytesIO()
        s3_client.download_fileobj(Bucket=bucket, Key=key, Fileobj=bytes_buffer)
        byte_value = bytes_buffer.getvalue()

        base64_image = base64.b64encode(byte_value)
        image_dict = {"image": base64_image}
    except:
        image_dict = {"image": b""}

    response.update(**image_dict)

    return {"statusCode": 200, "body": json.dumps(response)}
