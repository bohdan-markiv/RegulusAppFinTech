import boto3
import json
import logging
import openai

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_secret():

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

    logger.info(event)
    conversation_id = event["pathParameters"]["conversation_id"]
    event = json.loads(event['body'])
    filename = event["filename"]

    try:
        secret = get_secret()
        logger.info(type(secret))
        secret_value = secret["OpenAI API Key"]
        s3_client = boto3.client('s3')
        download_path = f"/tmp/{filename}"
        s3_client.download_file("conversations-admin", filename, download_path)

        client = openai.OpenAI(api_key=secret_value)

        with open(download_path, "rb") as file:
            response = client.files.create(
                file=file,
                purpose="assistants"
            )

        # Retrieve the file ID
        file_id = response.id
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
            'Access-Control-Allow-Origin': '*',
        },
        'body': json.dumps({"id": file_id,
                            "name": filename})
    }
