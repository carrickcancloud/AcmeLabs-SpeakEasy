import boto3
import json
from botocore.exceptions import ClientError
from typing import Dict, Any
from helpers.logger import set_log_level, logger

# Initialize Boto3 clients
s3 = boto3.client('s3')

# Function to handle the AWS Lambda invocation and check audio file existence in S3
def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    
    """Check the existence of audio files in S3 based on the synthesis results provided.

    Args:
        event (Dict[str, Any]): The input event containing results and bucket information.
        context (Any): The context object provided by AWS Lambda.

    Returns:
        Dict[str, Any]: A response dict containing status code and audio file statuses.
    """
    
    # Set log level from the event, default to DEBUG if not specified
    # Expecting logLevel to be one of 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'
    log_level = event.get('logLevel', 'DEBUG')
    set_log_level(log_level)

    # Log the invocation of the Lambda function
    logger.info("Check Audio File Existence function invoked.")

    # Log the received event
    logger.debug("Received event: %s", json.dumps(event))

    # Initialize the bucket variable
    bucket = None

    # Try to extract the bucket and synthesis results from the event
    try:
        
        # Extract bucket from the top-level event & log it
        bucket = event.get('bucket')
        logger.debug("Extracted bucket: %s", bucket)

        # Check if the bucket is provided
        if not bucket:
            
            # Log an error and return a failure response
            logger.error("No bucket name provided in the event.")

            # Return a response indicating failure
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'No bucket name provided'})
            }

        # Extract synthesis results from the event body
        synthesis_result = event.get('synthesisResult', {})

        # Log the synthesis result
        logger.debug("Extracted synthesis result: %s", synthesis_result)

        # Ensure synthesis_result is a dictionary and has a body key
        if isinstance(synthesis_result, dict) and 'body' in synthesis_result:

            # Extract the body from the synthesis result
            body = synthesis_result['body']
            
            # Log the body of the synthesis result
            logger.debug("Synthesis result body: %s", body)

            # Parse the body to get the results
            try:
                
                # Ensure body is a string and parse it as JSON and log it
                synthesis_results = json.loads(body).get('results', {})
                logger.debug("Parsed synthesis results: %s", synthesis_results)

            # Handle JSON decoding errors
            except json.JSONDecodeError as e:
                
                # Log the error and return a 400 response
                logger.error("Failed to decode JSON from synthesisResult body: %s", e)


                # Return a response indicating invalid JSON format
                return {
                    'statusCode': 400,
                    'body': json.dumps({'error': 'Invalid JSON in synthesisResult body'})
                }
            
        else:
            
            # Log an error if synthesis_result is not a valid dictionary or missing body
            logger.error("Invalid synthesisResult format.")

            # Return a response indicating invalid synthesisResult format
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Invalid synthesisResult format'})
            }

        # Initialize a dictionary to hold audio file statuses
        audio_statuses = {}

        # Check the existence of each audio file in S3
        for language, audio_key in synthesis_results.items():

            # Log the language and audio key being processed
            logger.debug("Processing language: %s", language)

            # Log the original audio key
            logger.debug("Original audio key: %s", audio_key)

            # Ensure audio_key is a valid S3 key
            if audio_key.startswith("s3://"):

                # Remove the "s3://" prefix and get the actual key after the bucket name & log it
                audio_key = audio_key[5:]
                audio_key = audio_key.split('/', 1)[1]
                logger.info("Checking existence of audio file: %s", audio_key)

            # If audio_key is not a valid S3 key, log an error and skip
            try:

                # Check if the audio file exists in the specified S3 bucket & log it
                response = s3.head_object(Bucket=bucket, Key=audio_key)
                logger.debug("S3 head_object response: %s", response)

                # If the file exists, update the audio_statuses dictionary
                audio_statuses[language] = 'EXISTS'

                # Log the successful existence check
                logger.info("Audio file exists: %s", audio_key)

            # Handle ClientError exceptions
            except ClientError as e:

                # Log the error and check if it's a 404 Not Found error
                if e.response['Error']['Code'] == '404':

                    # If the audio file does not exist, update the status
                    audio_statuses[language] = 'NOT_FOUND'

                    # Log the absence of the audio file
                    logger.warning("Audio file not found: %s", audio_key)

                else:

                    # If it's another error, log it and update the status
                    audio_statuses[language] = f'ERROR: {str(e)}'

                    # Log the error encountered while checking the audio file
                    logger.error("Error checking audio file: %s, Error: %s", audio_key, e)

        # Prepare the synthesis status result as a simple dictionary
        synthesis_status_result = {
            'statusCode': 200,
            'audio_statuses': audio_statuses
        }

        # Log audio file existence checks completion
        logger.info("Audio file existence checks completed.")

        # Log the synthesis status result before returning
        logger.debug("Synthesis status result before return: %s", json.dumps(synthesis_status_result))

        # Return the synthesis status result directly, ensuring it's a flat structure
        output = {
            'synthesisComplete': synthesis_status_result
        }

        # Log the final output before returning
        logger.debug("Final output before returning: %s", json.dumps(output))

        # Return the output with audio file statuses
        return output

    # Handle the finalization of the function
    finally:

        # Log the completion of the Lambda function execution
        logger.debug("Finished processing audio file existence check for bucket: %s", bucket if bucket else "Not Assigned")
