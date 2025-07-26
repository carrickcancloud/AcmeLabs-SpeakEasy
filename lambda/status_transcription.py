import boto3
import json
from botocore.exceptions import ClientError
from typing import Dict, Any, Optional
from helpers.logger import set_log_level, logger

# Initialize Boto3 clients
transcribe = boto3.client('transcribe')

# Function to handle the AWS Lambda invocation and check transcription job status
def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Optional[str]]:

    """Check the status of transcription jobs in AWS Transcribe.

    Args:
        event (Dict[str, Any]): The input event containing transcription result information.
        context (Any): The context object provided by AWS Lambda.

    Returns:
        Dict[str, Optional[str]]: A response dict containing job status and transcript URI if completed.
    """

    # Set log level from the event, default to DEBUG if not specified
    # Expecting logLevel to be one of 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'
    log_level = event.get('logLevel', 'DEBUG')
    set_log_level(log_level)

    # Log the invocation of the Lambda function
    logger.info("Check Transcription Status function invoked")

    # Log the received event
    logger.info("Received event: %s", json.dumps(event))

    # Extract job name from transcriptionResult
    transcription_result = event.get('transcriptionResult', {})
    job_name = transcription_result.get('job_name')

    # Check if job_name is provided
    if not job_name:

        # Log an error and return a failure response
        logger.error("No job name provided in the event.")

        # Return a response indicating failure
        return {'status': 'FAILED', 'message': 'Job name is required.'}

    # Check the body for errors
    body = json.loads(transcription_result.get('body', '{}'))

    # Check if the body contains an error
    if 'error' in body:

        # Log the error and return a failure response
        logger.error("Error in transcription result: %s", body['error'])

        # Return a response indicating failure
        return {'status': 'FAILED', 'message': body['message']}

    # Try to check the transcription job status
    try:

        # Log the start of the transcription job status check
        logger.info("Checking status of transcription job: %s", job_name)

        # Check the status of the transcription job
        response = transcribe.get_transcription_job(TranscriptionJobName=job_name)

        # Extract job status from the response & log it
        job_status = response['TranscriptionJob']['TranscriptionJobStatus']

        # Log the job status
        logger.info("Transcription job status: %s", job_status)

        # Prepare the response
        transcript_uri = response['TranscriptionJob']['Transcript']['TranscriptFileUri'] if job_status == 'COMPLETED' else None

        # Extract the bucket and key from the event
        bucket = event.get('bucket')
        key = event.get('key')

        # If key is provided, extract the original filename from it
        original_filename = key.split('/')[-1] if key else None

        # Log the prepared response details
        logger.debug("Preparing response with job status: %s, transcript URI: %s", job_status, transcript_uri)

        # Return the response with job status and transcript URI
        return {
            'status': job_status,
            'transcript_uri': transcript_uri,
            'bucket': bucket,
            'original_filename': original_filename,
            'job_name': job_name
        }

    # Handle ClientError exceptions
    except ClientError as e:

        # Log the error and return a structured error response
        logger.error("Error checking transcription job: %s", e)

        # Return an error response if the transcription job is not found or another error occurs
        return {'status': 'FAILED', 'message': 'An error occurred while checking the transcription job.'}

    # Handle unexpected exceptions
    except Exception as e:

        # Log the unexpected error and return a structured error response
        logger.error("Unexpected error: %s", e)

        # Return an error response for unexpected errors
        return {'status': 'FAILED', 'message': 'An unexpected error occurred.'}

    # Handle the finalization of the function
    finally:

        # Log the completion of the transcription job status check
        logger.debug("Finished processing transcription job status check for job name: %s", job_name)
