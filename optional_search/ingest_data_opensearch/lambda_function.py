import os
import boto3
from requests_aws4auth import AWS4Auth
from opensearchpy import OpenSearch, RequestsHttpConnection


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

def lambda_handler(event, context):
    document = {
        'title': event['title'],
        'description': event['description']
    }

    client.index(
        index = index_name,
        body = document,
        id = event['id']
    )

    return event
