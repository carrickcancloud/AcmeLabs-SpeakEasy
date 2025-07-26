import boto3
import json
import os
from botocore.exceptions import ClientError
from typing import Any, Dict
from helpers.logger import set_log_level, logger
from helpers.datetime_serializer import serialize_datetime

# Initialize Boto3 clients
stepfunctions = boto3.client('stepfunctions')

# Function to handle the AWS Lambda invocation and start a Step Functions execution
def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:

    """AWS Lambda function handler to start a Step Functions execution based on S3 event.

    Args:
        event (Dict[str, Any]): The event data from S3.
        context (Any): The context object provided by AWS Lambda.

    Returns:
        Dict[str, Any]: A response dictionary with status code and message.
    """

    # Set log level from the event, default to DEBUG if not specified
    # Expecting logLevel to be one of 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'
    log_level = event.get('logLevel', 'DEBUG')
    set_log_level(log_level)

    # Log the invocation of the Lambda function
    logger.info("Received event: %s", json.dumps(event))

    # Try to extract data from the event
    try:

        # Extract bucket and key from the S3 event
        bucket = event['Records'][0]['s3']['bucket']['name']
        key = event['Records'][0]['s3']['object']['key']

    # Handle KeyError
    except KeyError as e:

        # Log the error if bucket or key is missing
        logger.error("Missing key in event data: %s", e)

        # Return an error response if the bucket or key is not found
        return {
            'statusCode': 400,
            'body': json.dumps('Error: Missing required key in event data.')
        }

    # Log the extracted bucket and key
    logger.info("Extracted bucket: %s, key: %s", bucket, key)

    # Try to start the Step Functions execution
    try:

        # Log the preparation for starting the Step Functions execution
        logger.debug("Preparing to start Step Functions execution with bucket: %s, key: %s", bucket, key)

        # Ensure the state machine ARN is set in the environment variables
        # This should be set in the Lambda environment configuration
        # if 'STATE_MACHINE_ARN' not in os.environ:
        if 'STATE_MACHINE_ARN' not in os.environ:

            # Log an error if the ARN is not set
            logger.error("STATE_MACHINE_ARN environment variable is not set.")

            # Return an error response if the ARN is not set
            return {
                'statusCode': 500,
                'body': json.dumps('Error: STATE_MACHINE_ARN environment variable is not set.')
            }

        # Start the Step Functions execution with the provided bucket, key, and target languages
        response = stepfunctions.start_execution(
            stateMachineArn=os.environ['STATE_MACHINE_ARN'],
            input=json.dumps({
                'bucket': bucket,
                'key': key,
                'target_languages': ['es', 'fr', 'de']
            })
        )

        # Log the successful start of the Step Functions execution
        logger.info("Started Step Functions execution: %s", response['executionArn'])

        # Log the full response for debugging with serialization of datetime objects
        logger.debug("Step Functions response: %s", json.dumps(response, default=serialize_datetime))

        # Return a success response
        return {
            'statusCode': 200,
            'body': json.dumps('Step Function execution started!')
        }

    # Handle ClientError exceptions
    except ClientError as e:

        # Log the ClientError with traceback
        logger.error("ClientError while starting Step Functions execution for bucket: %s, key: %s. Error: %s", bucket,
                     key, e.response['Error']['Message'], exc_info=True)

        # Log the error with traceback
        return {
            'statusCode': 500,
            'body': json.dumps(f'ClientError: {e.response["Error"]["Message"]}')
        }

    # Handle unexpected exceptions
    except Exception as e:

        # Log the exception with traceback
        logger.critical("Critical error starting Step Functions execution for bucket: %s, key: %s. Error: %s", bucket,
                        key, str(e),
                        exc_info=True)

        # Log the error with traceback
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error starting Step Function execution: {str(e)}')
        }

    # Handle the finalization of the function
    finally:

        # Log the completion of the Lambda function execution
        logger.debug("Lambda function execution completed for bucket: %s, key: %s", bucket, key)
