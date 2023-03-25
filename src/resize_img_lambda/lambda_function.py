import boto3
import os
import io
import base64
from PIL import Image

s3 = boto3.client("s3")


def lambda_handler(event, context):
    base64_str = event["image"]
    if base64_str == "":
        image_path_dict = {"image_path": ""}
        event.update(**image_path_dict)
        return event

    try:
        imgdata = base64.b64decode(base64_str)
    except Exception:
        image_path_dict = {"image_path": ""}
        event.update(**image_path_dict)
        return event

    img = Image.open(io.BytesIO(imgdata))

    new_img = img.resize((128, 128))

    buffer = io.BytesIO()
    new_img.save(buffer, format="JPEG")

    buffer.seek(0)

    bucket = os.environ.get("S3_BUCKET", None)
    if not bucket:
        return {"statusCode": 500, "body": "Image could not be stored"}

    s3.upload_fileobj(buffer, bucket, f"{event['id']}.jpg")

    image_path_dict = {"image_path": f"s3://{bucket}/{event['id']}.jpg"}
    event.update(**image_path_dict)

    return event
