import os
import boto3
from boto3.dynamodb.types import TypeDeserializer
from requests_aws4auth import AWS4Auth
from opensearchpy import OpenSearch, RequestsHttpConnection

dynamo = boto3.client('dynamodb')

region = 'eu-west-1'
service = 'aoss'
credentials = boto3.Session().get_credentials()
awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)
host = os.environ.get('OPENSEARCH_HOST')
index_name = os.environ.get('INDEX_NAME')

# create an opensearch client and use the request-signer
client = OpenSearch(
    hosts=[{'host': host, 'port': 443}],
    http_auth=awsauth,
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection,
    pool_maxsize=20,
)


def delete_comments(ad):
    comments = dynamo.query(
        TableName='comments',
        KeyConditionExpression=f'ad_id = :ad_id',
        ExpressionAttributeValues={":ad_id": {'S': ad.get('id')}}
    )
    
    for comment in comments.get('Items'):
        dynamo.delete_item(
            TableName='comments',
            Key={'ad_id': comment.get('ad_id'), 'timestamp': comment.get('timestamp')}
        )

def delete_opensearch_ad(ad):
    client.delete(
        index = os.environ.get('INDEX_NAME'),
        id = ad.get('id')
    )

def lambda_handler(event, context):
    # To go from low-level format to python
    deserializer = TypeDeserializer()

    for record in event['Records']:
        if record['eventName'] == 'REMOVE':
            ad = {k: deserializer.deserialize(v) for k,v in record.get('dynamodb').get('Keys').items()}
            delete_opensearch_ad(ad)
            delete_comments(ad)
    
    return {
        'statusCode': 200
    }
