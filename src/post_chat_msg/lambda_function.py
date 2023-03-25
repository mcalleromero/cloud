import os
import json
import boto3
import time
from boto3.dynamodb.types import TypeDeserializer

dynamo = boto3.client("dynamodb")


def lambda_handler(event, context):
    user1 = event["user_id"]
    user2 = event["to"]
    msg = event["msg"]

    currtime = int(time.time())

    users_table = os.environ.get("USERS_TABLE", None)
    if not users_table:
        return {"statusCode": 500, "body": "Users table not found"}

    chats_table = os.environ.get("CHATS_TABLE", None)
    if not chats_table:
        return {"statusCode": 500, "body": "Users table not found"}

    chat = dynamo.query(
        TableName=users_table,
        KeyConditionExpression="user_id = :user_sender and begins_with(user_chat, :user_receiver)",
        ExpressionAttributeValues={
            ":user_sender": {"S": f"{user1}"},
            ":user_receiver": {"S": f"user:{user2}"},
        },
    )

    deserializer = TypeDeserializer()

    try:
        chat_info = chat.get("Items")[0]
        chat_parsed = {k: deserializer.deserialize(v) for k, v in chat_info.items()}
        chat_id = chat_parsed.get("user_chat").split(":")[-1]
    except IndexError:
        chat_id = f"{currtime}_{user1}"
        dynamo.put_item(
            TableName=users_table,
            Item={
                "user_id": {"S": user1},
                "user_chat": {"S": f"user:{user2}:chat:{chat_id}"},
            },
        )
        dynamo.put_item(
            TableName=users_table,
            Item={
                "user_id": {"S": user2},
                "user_chat": {"S": f"user:{user1}:chat:{chat_id}"},
            },
        )
    except Exception:
        return {
            "statusCode": 500,
            "body": json.dumps(f"[Err] Uncontrolled error while getting chat!!!"),
        }

    dynamo.put_item(
        TableName=chats_table,
        Item={
            "chat_id": {"S": chat_id},
            "timestamp": {"N": str(currtime)},
            "user": {"S": f"{user1}"},
            "msg": {"S": f"{msg}"},
        },
    )

    return {"statusCode": 200}
