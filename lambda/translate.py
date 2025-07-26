import boto3
import json
from botocore.exceptions import ClientError
from typing import Any, Dict, List
from datetime import datetime
from helpers.logger import set_log_level, logger

# Initialize Boto3 clients
translate = boto3.client('translate')
s3 = boto3.client('s3')

# Function to handle the AWS Lambda invocation and translate text from a transcript stored in S3
def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:

    """AWS Lambda function to translate text from a transcript stored in S3.

    Args:
        event (Dict[str, Any]): The input event containing parameters for translation.
        context (Any): The context object provided by AWS Lambda.

    Returns:
        Dict[str, Any]: A response dict containing status code and results or error message.
    """

    # Set log level from the event, default to DEBUG if not specified
    # Expecting logLevel to be one of 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'
    log_level = event.get('logLevel', 'DEBUG')
    set_log_level(log_level)

    # Log the invocation of the Lambda function
    logger.info("Translate function invoked")

    # Log the received event
    logger.info("Received event: %s", json.dumps(event))

    # Extract data from the event
    transcript_uri: str = event['transcript_uri']
    target_languages: List[str] = event['target_languages']
    bucket: str = event['bucket']
    original_filename: str = event.get('original_filename')

    # Log the extracted parameters
    logger.info("Extracted parameters - Bucket: %s, Original Filename: %s, Transcript URI: %s", bucket,
                original_filename, transcript_uri)

    # Check if the transcript URI is provided
    results: Dict[str, str] = {}

    # Try to process the translation
    try:

        # Log the transcript URI being processed
        logger.info("Retrieving transcript text from: %s", transcript_uri)

        # Extract the key from the transcript URI
        key = transcript_uri.split(f"s3.us-east-1.amazonaws.com/{bucket}/")[-1]

        # Log the extracted key
        logger.info("Extracted S3 Key: %s", key)

        # Check if the key is empty
        if not key:

            # Log an error if the key is empty
            logger.error("Extracted key is empty. Please check the transcript URI.")

            # Return an error response if the key is invalid
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Invalid transcript URI.'})
            }

        # Retrieve the transcript text from S3
        transcript_object = s3.get_object(Bucket=bucket, Key=key)
        transcript_text: str = transcript_object['Body'].read().decode('utf-8')

        # Log the successful retrieval of transcript text
        logger.info("Transcript text retrieved successfully.")

        # Check if the transcript text is empty
        for target_language in target_languages:

            # Log the target language being processed
            logger.info("Translating text to: %s", target_language)

            # Try to translate the text
            try:

                # Translate the text using Amazon Translate
                translated_text = translate.translate_text(
                    Text=transcript_text,
                    SourceLanguageCode='en',
                    TargetLanguageCode=target_language
                )

                # Generate a unique translation file name
                current_time = datetime.now().strftime('%Y%m%d_%H%M%S.%f')[:-3]
                translation_key: str = f'translations/{original_filename.split(".")[0]}_translation_{target_language}-{current_time}.txt'

                # Save the translated text to S3
                s3.put_object(Bucket=bucket, Key=translation_key, Body=translated_text['TranslatedText'])

                # Log the successful translation and storage
                logger.info("Translation successful for %s: s3://%s/%s", target_language, bucket, translation_key)

                # Store the result in the results dictionary
                results[target_language] = f's3://{bucket}/{translation_key}'

            # Handle ClientError exceptions
            except ClientError as e:

                # Log the error and store a failure message
                logger.error("Error during translation for %s: %s", target_language, e)

                # Store the error message in results
                results[target_language] = f'Translation failed for {target_language}. Error: {str(e)}'

            # Handle unexpected exceptions
            except Exception as e:

                # Log the unexpected error
                logger.error("An unexpected error occurred during translation for %s: %s", target_language, e)

                # Store the error message in results
                results[target_language] = f'Translation not found for {target_language}. Error: {str(e)}'

        # Log the completion of the translation process
        logger.info("Translation process completed for all target languages.")

        # Return the response with status code 200 and results
        return {
            'statusCode': 200,
            'bucket': bucket,
            'key': f'audio_inputs/{original_filename}',
            'target_languages': target_languages,
            'body': json.dumps({
                'results': results,
                'original_filename': original_filename
            })
        }

    # Handle ClientError exceptions
    except ClientError as e:

        # Log the error and return a structured error response
        logger.error("Error retrieving transcript or translating text: %s", e)

        # Return an error response if the transcript file is not found or another error occurs
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
            'body': json.dumps({'error': 'An unexpected error occurred'})
        }

    # Handle the finalization of the function
    finally:

        # Log the completion of the Lambda function execution
        logger.debug("Finished processing translation for original filename: %s", original_filename)
