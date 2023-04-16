"""TODO"""
import json
import logging
import os
from typing import Any, Dict, List, Union

import boto3

logger = logging.getLogger(__name__)

dynamodb_client = boto3.client("dynamodb")

DYNAMODB_TABLE_NAME: str = os.environ["DYNAMODB_TABLE_NAME"]


def lambda_handler(event: Dict[str, Any], _) -> Dict[str, Union[int, str]]:
    """TODO"""
    event_records: List[Dict[str, str]] = event["Records"]

    logger.info(f"Processing records: {event_records}")
    for record in event_records:
        record_body: Dict[str, str] = json.loads(record["body"])
        dynamodb_client.put_item(
            TableName=DYNAMODB_TABLE_NAME,
            Item={
                "message_id": {"N": record_body["message_id"]},
                **{
                    key: {"S": val}
                    for key, val in record_body.items() if key != "message_id"
                }
            }
        )

    return {
        "statusCode": 200,
        "body": json.dumps("Successfully put new dynamodb records!")
    }
