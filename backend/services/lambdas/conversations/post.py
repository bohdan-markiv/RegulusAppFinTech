import boto3
import json
import logging
import uuid

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def lambda_handler(event, _):
    """This lambda is responsible for creating new conversation in DynamoDB.

    Args:
        event (json): json event which is automatically attached by aws. Doesn't bring information.
        _ (json): the placeholder is necessary for context, also aws thing. Not used.

    Returns:
        json: response with either mistake code, or new conversation id.
    """

    new_conversation_id = str(uuid.uuid4())

    try:

        dynamodb = boto3.client('dynamodb', region_name='eu-central-1')
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': f"Unexpected error - {e}"
        }

    try:
        dynamodb.put_item(TableName='conversations',
                          Item={
                              "id": {
                                  "S": new_conversation_id
                              },
                              "title": {
                                  "S": "New Chat"
                              },
                              "thread_id": {
                                  "S": ""
                              },
                              "assistant_id": {
                                  "S": ""
                              },
                              "user_id": {
                                  "S": "admin"
                              },
                              "messages": {
                                  "L": []
                              }
                          })
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': f"Unexpected error - {e}"
        }

    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': new_conversation_id
    }
