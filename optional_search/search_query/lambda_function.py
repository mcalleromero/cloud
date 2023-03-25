import os
import boto3
import json
from requests_aws4auth import AWS4Auth
from opensearchpy import OpenSearch, RequestsHttpConnection, Search


region = "eu-west-1"
service = "aoss"
credentials = boto3.Session().get_credentials()
awsauth = AWS4Auth(
    credentials.access_key,
    credentials.secret_key,
    region,
    service,
    session_token=credentials.token,
)
host = os.environ.get("OPENSEARCH_HOST")
index_name = os.environ.get("INDEX_NAME")

# create an opensearch client and use the request-signer
client = OpenSearch(
    hosts=[{"host": host, "port": 443}],
    http_auth=awsauth,
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection,
    pool_maxsize=20,
)


def hits_iter(hits):
    for hit in hits:
        yield {"id": hit.meta.id, "title": hit.title, "description": hit.description}


def lambda_handler(event, context):
    query_phrase = event["search"]

    s = Search(using=client, index=index_name).update_from_dict(
        {
            "size": 10,
            "query": {
                "multi_match": {
                    "query": query_phrase,
                    "fields": ["title^2", "description"],
                },
            },
        }
    )

    response = s.execute()
    hits = list(hits_iter(response))

    return {"statusCode": 200, "body": json.dumps(hits)}
