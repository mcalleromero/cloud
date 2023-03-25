import os
import boto3
import json
import logging

stepfunctions = boto3.client("stepfunctions")


def start(state_machine_arn, run_input):
    try:
        stepfunctions.start_execution(
            stateMachineArn=state_machine_arn, input=run_input
        )
    except Exception as err:
        logging.error(
            "Couldn't start state machine %s. Here's why: %s: %s",
            state_machine_arn,
            err.response["Error"]["Code"],
            err.response["Error"]["Message"],
        )
        return {"statusCode": 500, "body": "Unexpected error while storing ad"}

    return {"statusCode": 200}


def lambda_handler(event, context):
    state_machine_arn = os.environ.get("STATE_MACHINE_ARN")
    try:
        event["price"] = str(event["price"])
    except Exception as e:
        return {"statusCode": 500, "body": e}

    run_input = json.dumps(event)
    response = start(state_machine_arn, run_input)
    return response
