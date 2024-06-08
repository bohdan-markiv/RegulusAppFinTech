import boto3
import json
import logging
import openai

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
    """This lambda is responsible for downloading the uploaded file from the AWS S3 bucket, and upload it to OpenAI
    storage.  

    Args:
        event (json): json file, which contains information about the Path Parameter. This parameter is used
        to get an id of the conversation. Moreover, in the body of the event is located the name of the attached file.
        _ (json): the placeholder is necessary for context, also aws thing. Not used.

    Returns:
        json: response with either mistake code, or the the uploaded file id.
    """
    event = json.loads(event['body'])
    filename = event["filename"]

    try:

        # Get selected file from S3.
        secret = get_secret()
        secret_value = secret["OpenAI API Key"]
        s3_client = boto3.client('s3')
        download_path = f"/tmp/{filename}"
        s3_client.download_file("conversations-admin", filename, download_path)

        # Connect to OpenAI and upload there the file.
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
