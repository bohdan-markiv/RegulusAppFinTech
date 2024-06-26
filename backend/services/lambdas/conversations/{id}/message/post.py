import boto3
import json
import logging
import requests
from utils.generate_response import GenerateResponse

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_secret():
    """This function is responsible for getting the secret value - openai api key
    from aws secret manager.

    Returns:
        json: dictionary with secret values.
    """
    secret_name = "OpenAiKey"
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
    return json.loads(secret)


def lambda_handler(event, _):
    """This function is responsible for putting user and bot's messages to the conversation in dynamo db. 

    Args:
        event (json): json file, which contains information about the Path Parameter. This parameter is used
        to get an id of the conversation. Moreover, in the body of the event the user prompt can be found,
        and information about the attached files. 
        _ (json): the placeholder is necessary for context, also aws thing. Not used.

    Returns:
        json: response with either mistake code, or the the generated response.
    """
    logger.info(event)
    conversation_id = event["pathParameters"]["conversation_id"]
    event = json.loads(event['body'])
    message = event["message"]
    file = event["file"]

    try:

        # Here the details about the thread id and assistant id of the conversation are extracted.
        response = requests.get(
            f"https://vjwir58s9d.execute-api.eu-central-1.amazonaws.com/prod/conversations/{conversation_id}")
        response_body = json.loads(response.content)
        thread_id, assistant_id = response_body["thread_id"], response_body["assistant_id"]
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

        dynamodb = boto3.client('dynamodb', region_name='eu-central-1')
        secret = get_secret()
        logger.info(type(secret))
        secret_value = secret["OpenAI API Key"]

        # This class generates OpenAI response on the users prompt.
        generated_response = GenerateResponse(
            message, secret_value, thread_id, assistant_id, file)

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

        # Here we adjust the style of input message to be acceptable by DynamoDB.
        initial_message = generated_response.generate_input_message()

        # Scan the table to get all items
        response = dynamodb.update_item(
            TableName='conversations',
            Key={
                'id': {'S': conversation_id},
                'user_id': {'S': "admin"}
            },
            UpdateExpression="SET messages = list_append(messages, :m)",
            ExpressionAttributeValues={
                ':m': {'L': [initial_message]}
            },
            ReturnValues="UPDATED_NEW"
        )

    except Exception as e:
        logger.error(f"error - {e}", exc_info=True)
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': f"Unexpected error while inserting initial message- {e}"
        }
    try:

        # Here we generate answer by OpenAI and prepare it to be sent to DynamoDB.
        response_message = generated_response.get_response_from_openai()

        # Scan the table to get all items
        response = dynamodb.update_item(
            TableName='conversations',
            Key={
                'id': {'S': conversation_id},
                'user_id': {'S': "admin"}
            },
            UpdateExpression="""SET messages = list_append(messages, :m),
                                thread_id = :t, 
                                assistant_id = :a""",
            ExpressionAttributeValues={
                ':m': {'L': [response_message]},
                ':t': {'S': generated_response.thread_id},
                ':a': {'S': generated_response.assistant_id}
            },
            ReturnValues="UPDATED_NEW")

    except Exception as e:
        logger.error(f"error - {e}", exc_info=True)
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': f"Unexpected error while inserting response message- {e}"
        }

    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
        },
        'body': generated_response.messages}
