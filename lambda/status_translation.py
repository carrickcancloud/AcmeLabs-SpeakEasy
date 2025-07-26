import boto3
import json
from botocore.exceptions import ClientError
from typing import Dict, Any
from helpers.logger import set_log_level, logger

# Initialize Boto3 clients
s3 = boto3.client('s3')

# Function to handle the AWS Lambda invocation and check translation status in S3
def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:

    """Check the status of translations in S3.

    Args:
        event (Dict[str, Any]): The input event containing results and bucket information.
        context (Any): The context object provided by AWS Lambda.

    Returns:
        Dict[str, Any]: A response dict containing status code and translation statuses.
    """

    # Set log level from the event, default to DEBUG if not specified
    # Expecting logLevel to be one of 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'
    log_level = event.get('logLevel', 'DEBUG')
    set_log_level(log_level)

    # Log the invocation of the Lambda function
    logger.info("Check Translation Status function invoked")

    # Log the received event
    logger.info("Received event: %s", json.dumps(event))

    # Extract data from the event
    bucket = event.get('bucket')

    # Initialize target languages from the event or use an empty list
    target_languages = event.get('target_languages', [])

    # Extract original filename and results from the event body
    body = event.get('body', '{}')

    # Try to parse the body as JSON
    try:

        # Parse the body to extract original filename and results
        body = json.loads(body)
        original_filename = body.get('original_filename')
        results = body.get('results', {})

        # If target_languages are provided in the body, update the list
        if 'target_languages' in body:
            target_languages = body.get('target_languages', target_languages)

    # Handle JSON decoding errors
    except json.JSONDecodeError as e:
        # Log the error and return a 400 response
        logger.error("Error decoding JSON from body: %s", e)

        # Return a response indicating invalid body format
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Invalid body format.'})
        }

    # Check for required parameters
    if not bucket or not original_filename or not target_languages:

        # Log an error and return a 400 response
        logger.error("Missing required parameters in the event.")

        # Return a response indicating missing parameters
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Bucket, original filename, and target languages are required.'})
        }

    # Initialize a flag to track if all translations exist
    all_translations_exist = True

    # Initialize a dictionary to hold translation results
    translation_results = {}

    # Try to check the existence of translation files in S3
    try:

        # Loop through each target language to check for translation files
        for target_language in target_languages:

            # Get the expected translation file URL from the results
            translation_file_url = results.get(target_language)

            # If the translation file URL is provided, check its existence
            if translation_file_url:

                # Log the translation file URL being checked
                translation_key = translation_file_url.replace(f"s3://{bucket}/", "")
                logger.info("Checking for translation file: %s", translation_key)

                # Try to check if the translation file exists in S3
                try:

                    # Attempt to head the object to check its existence
                    s3.head_object(Bucket=bucket, Key=translation_key)

                    # If successful, mark the translation as existing
                    translation_results[target_language] = f'Translation exists for {target_language}.'

                    # Log the successful existence check
                    logger.info("Translation file found for %s: %s", target_language, translation_file_url)

                # Handle ClientError exceptions
                except ClientError as e:

                    # If the error is a 404, the translation file does not exist
                    if e.response['Error']['Code'] == '404':

                        # Store the result indicating the translation does not exist
                        translation_results[target_language] = f'Translation not found for {target_language}.'

                        # Mark as not existing if a 404 error occurs
                        all_translations_exist = False

                        # Log the warning for missing translation file
                        logger.warning("Translation file not found for %s: %s", target_language, translation_key)

                    else:

                        # Log the error for other types of ClientError
                        logger.error("Error checking translation file: %s", e)

                        # Store the error message in the results
                        translation_results[target_language] = f'Error checking status for {target_language}.'

                        # Mark as not existing if an error occurs
                        all_translations_exist = False

            else:

                # If no translation file URL is provided, store a message indicating it
                translation_results[target_language] = f'Translation not found for {target_language}.'

                # Mark as not existing if no URL is provided
                all_translations_exist = False

                # Log the warning for missing translation file URL
                logger.warning("No translation file URL provided for %s.", target_language)

        # Determine the overall status
        status = "COMPLETED" if all_translations_exist else "IN_PROGRESS"
        status_code = 200

        # Log the overall status of the translation check
        logger.info("Translation status check completed. Overall status: %s", status)

        # Return the response with the status code, bucket, key, target languages, and results
        return {
            'statusCode': status_code,
            'bucket': bucket,
            'key': f'audio_inputs/{original_filename}',
            'target_languages': target_languages,
            'body': json.dumps({
                'results': translation_results,
                'original_filename': original_filename
            }),
            'statusTranslationResult': {
                'statusCode': status_code,
                'body': json.dumps({'status': status})
            },
            'status': status
        }

    # Handle ClientError exceptions
    except ClientError as e:

        # Log the error and return a structured error response
        logger.error("Error checking translation status: %s", e)

        # Return an error response if the S3 ClientError occurs
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

    # Handle unexpected exceptions
    except Exception as e:

        # Log the unexpected error and return a structured error response
        logger.error("An unexpected error occurred: %s", e)

        # Return an error response for unexpected errors
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'An unexpected error occurred.'})
        }

    # Handle the finalization of the function
    finally:

        # Log the completion of the Lambda function execution
        logger.debug("Finished processing translation status check for original filename: %s", original_filename)
