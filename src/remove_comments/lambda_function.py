import os
import boto3
from boto3.dynamodb.types import TypeDeserializer

dynamo = boto3.client("dynamodb")


def delete_comments(comments_table, ad):
    comments = dynamo.query(
        TableName=comments_table,
        KeyConditionExpression=f"ad_id = :ad_id",
        ExpressionAttributeValues={":ad_id": {"S": ad.get("id")}},
    )

    for comment in comments.get("Items"):
        dynamo.delete_item(
            TableName=comments_table,
            Key={"ad_id": comment.get("ad_id"), "timestamp": comment.get("timestamp")},
        )


def lambda_handler(event, context):
    # To go from low-level format to python
    deserializer = TypeDeserializer()

    comments_table = os.environ.get("COMMENTS_TABLE", None)
    if not comments_table:
        return {"statusCode": 500, "body": "Error finding comments table"}

    for record in event["Records"]:
        if record["eventName"] == "REMOVE":
            ad = {
                k: deserializer.deserialize(v)
                for k, v in record.get("dynamodb").get("Keys").items()
            }
            delete_comments(comments_table, ad)

    return {"statusCode": 200}
