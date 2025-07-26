import boto3
import json
import time
from botocore.exceptions import ClientError
from typing import Dict, Any
from datetime import datetime
from helpers.logger import set_log_level, logger

# Initialize Boto3 clients
s3 = boto3.client('s3')
transcribe = boto3.client('transcribe')

# Function to handle the AWS Lambda invocation and start a transcription job
def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:

    """AWS Lambda function to handle audio transcription using Amazon Transcribe.

    Args:
        event (Dict[str, Any]): The event data containing the S3 bucket and key.
        context (Any): The context object provided by AWS Lambda.

    Returns:
        Dict[str, Any]: A response object containing the status code and body.
    """

    # Set log level from the event, default to DEBUG if not specified
    # Expecting logLevel to be one of 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'
    log_level = event.get('logLevel', 'DEBUG')
    set_log_level(log_level)

    # Log the invocation of the Lambda function
    logger.info("Transcribe function invoked")

    # Log the received event
    logger.info("Received event: %s", json.dumps(event))

    # Try to extract data from the event
    try:

        # Extract bucket, key, and original filename from the event
        bucket = event['bucket']
        key = event['key']
        original_filename = key.split('/')[-1]

    # Handle KeyError
    except KeyError as e:

        # Log the error if bucket or key is missing
        logger.error("Missing key in event data: %s", e)

        # Return an error response if the bucket or key is not found
        return {'statusCode': 400, 'body': json.dumps({'error': 'Missing required key in event data.'})}

    # Log the extracted bucket and key
    logger.info("Checking existence of object in bucket: %s, key: %s", bucket, key)

    # Generate a unique job name based on the original filename and current timestamp
    base_name = original_filename.split('.')[0]
    job_name = f"{base_name}-{int(time.time())}"

    # Try to check if the S3 object exists and start the transcription job
    try:

        # Check if the S3 object exists
        s3.head_object(Bucket=bucket, Key=key)
        logger.info("Object exists: s3://%s/%s", bucket, key)

        # Log the start of the transcription job
        logger.info("Starting transcription job: %s", job_name)

        # Define the LanguageCode variable
        languagecode = 'en-US'

        # Get the current timestamp in the desired format & log it
        current_time = datetime.now().strftime('%Y%m%d_%H%M%S.%f')[:-3]
        logger.info("Current timestamp: %s", current_time)

        # Start the transcription job with output specified
        transcribe.start_transcription_job(
            TranscriptionJobName=job_name,
            Media={'MediaFileUri': f's3://{bucket}/{key}'},
            MediaFormat='mp3',
            LanguageCode=languagecode,
            OutputBucketName=bucket,
            OutputKey=f'transcripts/{base_name}_transcript_{languagecode}-{current_time}.txt'
        )

        # Poll for job completion
        while True:

            # Log the status check for the transcription job
            logger.info("Checking status of transcription job: %s", job_name)

            # Get the transcription job status
            response = transcribe.get_transcription_job(TranscriptionJobName=job_name)
            job_status = response['TranscriptionJob']['TranscriptionJobStatus']

            # Log the current job status
            if job_status in ['COMPLETED', 'FAILED']:

                # Break the loop if the job is completed or failed
                break

            # Log the current job status and wait before checking again
            logger.info("Transcription job status: %s", job_status)

        # Check the final status of the transcription job
        if job_status == 'COMPLETED':

            # Log the completion of the transcription job & log it
            transcript_uri = response['TranscriptionJob']['Transcript']['TranscriptFileUri']
            logger.info("Transcription job completed: %s", transcript_uri)

            # Construct the expected transcript key based on the naming convention & log it
            transcript_key = f'transcripts/{base_name}_transcript_{languagecode}-{current_time}.txt'
            logger.info("Expected transcript key: %s", transcript_key)

            # Try to fetch the transcript from S3
            try:

                # Fetch the transcript directly from the S3 bucket
                transcript_response = s3.get_object(Bucket=bucket, Key=transcript_key)
                transcript_data = json.loads(transcript_response['Body'].read().decode('utf-8'))

                # Extract only the transcribed text
                transcript_text = transcript_data['results']['transcripts'][0]['transcript']

                # Save the transcript text to a new file
                s3.put_object(
                    Bucket=bucket,
                    Key=transcript_key,
                    Body=transcript_text
                )

                # Log the successful saving of the transcript
                logger.info("Transcript saved to: s3://%s/%s", bucket, transcript_key)

                # Return a structured response with the job name, status code, and transcript URI
                return {
                    'job_name': job_name,
                    'statusCode': 200,
                    'body': json.dumps({
                        'transcript_uri': f's3://{bucket}/{transcript_key}',
                        'bucket': bucket,
                        'original_filename': original_filename
                    })
                }

            # Handle ClientError exceptions
            except ClientError as e:

                # Log the error and return a structured error response
                logger.error("Error fetching transcript from S3: %s", e)

                # Return an error response if the transcript file is not found
                return {'statusCode': 500, 'body': json.dumps({'error': 'S3 ClientError', 'message': str(e)})}

        else:

            # Log the failure of the transcription job & log it
            failure_reason = response['TranscriptionJob'].get('FailureReason', 'Unknown error')
            logger.error("Transcription job failed: %s", failure_reason)

            # Return an error response with the failure reason
            return {'statusCode': 500,
                    'body': json.dumps({'error': 'Transcription job failed', 'reason': failure_reason})}

    # Handle ClientError exceptions
    except ClientError as e:

        # Log the error and return a structured error response
        logger.error("Error checking object existence: %s", e)

        # Return an error response if the object does not exist
        return {'statusCode': 500, 'body': json.dumps({'error': 'S3 ClientError', 'message': str(e)})}

    # Handle unexpected exceptions
    except Exception as e:

        # Log the unexpected error and return a structured error response
        logger.critical("An unexpected error occurred: %s", e)

        # Return an error response for unexpected errors
        return {'statusCode': 500, 'body': json.dumps({'error': 'Internal Server Error', 'message': str(e)})}

    # Handle the finalization of the function
    finally:

        # Log the completion of the Lambda function execution
        logger.debug("Lambda function execution completed for bucket: %s, key: %s", bucket, key)
