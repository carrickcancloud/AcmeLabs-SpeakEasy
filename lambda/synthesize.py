import boto3
import json
from botocore.exceptions import ClientError
from typing import Dict, Any
from datetime import datetime
from helpers.logger import set_log_level, logger

# Initialize Boto3 clients
s3 = boto3.client('s3')
polly = boto3.client('polly')

# Map of target languages to their respective Polly voices
language_voice_map = {
    "es": "Lucia",  # Spanish
    "fr": "Celine",  # French
    "de": "Marlene"  # German
}

# Function to handle the AWS Lambda invocation and synthesize speech from translated texts
def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:

    """AWS Lambda function to synthesize speech from translated texts.

    Args:
        event (Dict[str, Any]): The input event containing bucket and original filename.
        context (Any): The context object provided by AWS Lambda.

    Returns:
        Dict[str, Any]: A response dict containing status code and results.
    """

    # Set log level from the event, default to DEBUG if not specified
    # Expecting logLevel to be one of 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'
    log_level = event.get('logLevel', 'DEBUG')
    set_log_level(log_level)

    # Log the invocation of the Lambda function
    logger.info("Synthesize function invoked")

    # Log the received event
    logger.info("Received event: %s", json.dumps(event))

    # Extract bucket from the event
    bucket: str = event.get('bucket')

    # Extract original_filename from the body
    original_filename: str = None

    # Try to parse the body from the event
    try:

        # Ensure body is a string and parse it
        body = json.loads(event.get('body', '{}'))

        # Extract original filename from the body
        original_filename = body.get('original_filename')

    # Handle JSON decoding errors
    except json.JSONDecodeError as e:

        # Log the error and return a 400 response
        logger.error("Failed to decode JSON from body: %s", e)

        # Return a response indicating invalid body format
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Invalid JSON in body'})
        }

    # Check if bucket is provided
    if not bucket:

        # Log an error and return a 400 response
        logger.error("Bucket name is missing in the event.")

        # Return a response indicating missing bucket name
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Bucket name is required.'})
        }

    # Check if original_filename is provided
    if not original_filename:

        # Log an error and return a 400 response
        logger.error("Original filename is missing in the event.")

        # Return a response indicating missing original filename
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Original filename is required.'})
        }

    # Parse the body to get translated texts
    translated_texts: Dict[str, str] = {}

    # Extract translated texts for each target language
    for lang in ['es', 'fr', 'de']:

        # Get the translated text for the language from the body
        translated_texts[lang] = body.get('results', {}).get(lang, '')

    # Initialize a dictionary to hold synthesis results
    results: Dict[str, str] = {}

    # Check if any translated texts are provided
    if not any(translated_texts.values()):

        # Log an error and return a 400 response
        logger.error("No translated texts provided for synthesis.")

        # Return a response indicating no translations available
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'No translations available'})
        }

    # Try to synthesize speech for each target language
    try:

        # Get the current timestamp for file naming & log it
        current_time = datetime.now().strftime('%Y%m%d_%H%M%S.%f')[:-3]
        logger.info("Current timestamp for file naming: %s", current_time)

        # Loop through each target language and synthesize speech
        for target_language, translated_text in translated_texts.items():

            # Log the target language being processed
            if not translated_text:

                # Log a warning if no translated text is found for the language
                logger.warning("No translated text found for language: %s", target_language)

                # Skip to the next language if no text is available
                continue

            # Log the synthesis process for the target language
            logger.info("Synthesizing speech for language: %s", target_language)

            # Get the corresponding voice ID for the target language
            voice_id = language_voice_map.get(target_language)

            # Check if a voice is available for the target language
            if not voice_id:

                # Log an error if no voice is available for the language
                logger.error("No voice available for language: %s", target_language)

                # Return a response indicating no voice available
                return {
                    'statusCode': 400,
                    'body': json.dumps({'error': f'No voice available for language: {target_language}'})
                }

            # Log the voice ID being used
            audio_key: str = f'audio_outputs/{original_filename.split(".")[0]}_{target_language}-{current_time}.mp3'
            logger.info("Generated audio key: %s", audio_key)

            # Try to synthesize speech using Amazon Polly
            try:

                # Call the Polly synthesize_speech API
                response = polly.synthesize_speech(
                    Text=translated_text,
                    OutputFormat='mp3',
                    VoiceId=voice_id
                )

                # Log the successful synthesis response
                logger.info("Synthesis response received for language: %s", target_language)

                # Save the audio to S3
                s3.put_object(Bucket=bucket, Key=audio_key, Body=response['AudioStream'].read())

                # Log the successful storage of synthesized speech
                logger.info("Synthesized speech saved to: s3://%s/%s", bucket, audio_key)

                # Store the audio key for future reference
                results[target_language] = audio_key

            # Handle ClientError exceptions
            except ClientError as e:

                # Log the error and return a 500 response
                logger.error("Client error while synthesizing speech for %s: %s", target_language, e)

                # Return a response indicating client error
                return {
                    'statusCode': 500,
                    'body': json.dumps({'error': f'Client error occurred while synthesizing for {target_language}'})
                }

        # Log the successful completion of all syntheses
        logger.info("All syntheses completed successfully.")

        # Return the response with the synthesis results
        return {
            'statusCode': 200,
            'body': json.dumps({
                'results': results,
                'original_filename': original_filename,
                'bucket': bucket
            })
        }

    # Handle unexpected exceptions
    except Exception as e:

        # Log the unexpected error
        logger.error("An unexpected error occurred in synthesis: %s", e)

        # Return a structured error response
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'An unexpected error occurred'})
        }

    # Handle the finalization of the function
    finally:

        # Log the completion of the synthesis process
        logger.debug("Finished processing synthesis for original filename: %s", original_filename)
