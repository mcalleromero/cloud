import os
import simplejson as json
import boto3
from boto3.dynamodb.types import TypeDeserializer

dynamo = boto3.client("dynamodb")


def get_msgs_from_chat_iter(deserializer, messages):
    for msg in messages.get("Items"):
        yield {k: deserializer.deserialize(v) for k, v in msg.items()}


def lambda_handler(event, context):
    user1 = event["user_id"]
    user2 = event["from"]

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
        return {
            "statusCode": 404,
            "body": json.dumps(f"There is no chat between {user1} and {user2}"),
        }
    except Exception:
        return {
            "statusCode": 500,
            "body": json.dumps(f"[Err] Uncontrolled error while getting chat!!!"),
        }

    messages_dyn = dynamo.query(
        TableName=chats_table,
        KeyConditionExpression="chat_id = :chat_id",
        ExpressionAttributeValues={":chat_id": {"S": f"{chat_id}"}},
    )

    messages = list(get_msgs_from_chat_iter(deserializer, messages_dyn))

    return {"statusCode": 200, "body": json.dumps(messages)}
