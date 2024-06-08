import boto3
import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, _):
    """This lambda is responsible for changing the title of the conversation.

    Args:
        event (json): json file, which contains information about the Path Parameter. This parameter is used
        to get an id of the conversation, for which the title is changed.
        _ (json): the placeholder is necessary for context, also aws thing. Not used.

    Returns:
        json: response with either mistake code, or the the title.
    """
    logger.info(event)
    conversation_id = event["pathParameters"]["conversation_id"]
    event = json.loads(event['body'])
    title = event["title"]

    try:

        dynamodb = boto3.client('dynamodb', region_name='eu-central-1')

        # Scan the table to get all items
        dynamodb.update_item(
            TableName='conversations',
            Key={
                'id': {'S': conversation_id},
                'user_id': {'S': "admin"}
            },
            UpdateExpression="SET title = :t",
            ExpressionAttributeValues={
                ':t': {'S': title}
            },
            ReturnValues="UPDATED_NEW")
        logger.info(f"New title - {title}")

    except Exception as e:
        logger.error(f"error - {e}", exc_info=True)
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
        'body': title
    }
