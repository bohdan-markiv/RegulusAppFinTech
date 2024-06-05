import boto3
import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_secret():

    secret_name = "aws-secret"
    region_name = "eu-central-1"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except Exception as e:
        # For a list of exceptions thrown, see
        # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        raise e

    secret = get_secret_value_response['SecretString']
    final = json.loads(secret)
    logger.info(final)
    return {
        "accessKeyId": final["accessKeyId"],
        "secretAccessKey": final["secretAccessKey"]
    }


def transform_dynamodb_response(response):
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

    logger.info(event)
    conversation_id = event["pathParameters"]["conversation_id"]

    try:

        dynamodb = boto3.client('dynamodb', region_name='eu-central-1')

        # Scan the table to get all items
        response = dynamodb.scan(
            TableName='conversations',
            FilterExpression='id = :id',
            ExpressionAttributeValues={':id': {'S': conversation_id}})

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
        items = response.get('Items', [])[0]
        items = transform_dynamodb_response(items)
        secret = get_secret()
        items.update(secret)

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
        'body': json.dumps(items)
    }
