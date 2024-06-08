import boto3
import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def transform_dynamodb_response(response):
    """This function translates the type of response from DynamoDB into acceptable to a normal json.

    Args:
        response (json): scan of dynamo db result, which contains information about the conversation.

    Returns:
        json: transformed dynamo db response.
    """
    messages = []
    if response['messages'] != []:
        for message in response['messages']['L']:
            edited_message = message['M']
            messages.append({
                "text": edited_message["text"]["S"],
                "sender": edited_message["sender"]["S"],
                "timestamp": edited_message["timestamp"]["S"],
            })
    return {
        'id': response['id']['S'],
        'text': messages,
        'user_id': response['user_id']['S'],
        'title': response['title']['S'],
        'thread_id': response['thread_id']['S'],
        'assistant_id': response['assistant_id']['S']
    }


def lambda_handler(event, _):
    """This lambda is responsible for getting all the available conversations.

    Args:
        event (json): json event which is automatically attached by aws. Doesn't bring information.
        _ (json): the placeholder is necessary for context, also aws thing. Not used.

    Returns:
        json: response with either mistake code, or the list with conversation ids.
    """
    try:

        dynamodb = boto3.client('dynamodb', region_name='eu-central-1')

        # Scan the table to get all items
        response = dynamodb.scan(TableName='conversations')
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

    try:
        logger.info(response)
        items = response.get('Items', [])
        items = [transform_dynamodb_response(item) for item in items]

        result = []

        #  Here it is ensured, that only id and title of the conversations are passed, no other data.
        for item in items:
            result.append({
                "id": item["id"],
                "title": item["title"]
            })
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
        'body': json.dumps(result)
    }
