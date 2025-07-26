# 🎤 AcmeLabs SpeakEasy

Welcome to the AcmeLabs SpeakEasy project!

This project leverages GitHub Actions with AWS services to transcribe, translate, and synthesize audio files into French, German and Spanish. Below are the steps to set up your environment and deploy the resources.

AWS Services:
- AWS CloudFormation
- AWS CloudWatch
- AWS IAM
- AWS Lambda
- AWS Step Functions
- AWS Transcribe
- AWS Translate
- AWS Polly
- AWS S3

GitHub Services:
- GitHub Actions
- GitHub Repositories
- GitHub Secrets
- GitHub Workflows

Languages:
- 🐚 Bash (Inline Shell Scripts)
- 📄 YAML
- 🐍 Python 

## Table of Contents
- [🎤 AcmeLabs SpeakEasy](#-acmelabs-speakeasy)
  - [Table of Contents](#table-of-contents)
  - [🌐 Setup AWS Credentials](#-setup-aws-credentials)
  - [👤 Create IAM User](#-create-iam-user)
  - [🔑 Create Access Keys](#-create-access-keys)
  - [📄 Create IAM Policy](#-create-iam-policy)
  - [🔐 Configure GitHub Secrets](#-configure-github-secrets)
  - [🔧 Modify Configuration Files](#-modify-configuration-files)
  - [📦 GitHub Repository Structure](#-github-repository-structure)
  - [🔀 Create beta Branch](#-create-beta-branch)
  - [🚀 Deploy Resources](#-deploy-resources)
  - [💣 Destroy Resources](#-destroy-resources)
  - [🚧 Update Resources](#-update-resources)
  - [🔄 Trigger Audio Processing](#-trigger-audio-processing)
  - [🏁 Conclusion](#-conclusion)

## 🌐 Setup AWS Credentials
To set up AWS credentials follow these steps:
1. **AWS Account**: Ensure you have an AWS account. If not, create one at [AWS](https://aws.amazon.com/).
   
## 👤 Create IAM User
To create an IAM user with the necessary permissions for GitHub Actions, follow these steps:
- Create an IAM user in the AWS Management Console with programmatic access.
- Example IAM username: `<Project>_speakeasy_github_actions_user`

1. Sign in to the [AWS Management Console](https://aws.amazon.com/console/).
2. Navigate to the IAM service.
3. Click on "Users" in the sidebar, then click on "Create user".
4. Enter a username for the new user and click on "Next" to proceed to the **Set permissions** section.
5. Click on "Next" to proceed to the "Review and create" section.
6. Click "Create user" to proceed.

## 🔑 Create Access Keys
To create access keys for the IAM user you just created, follow these steps:
1. Navigate to the "Security credentials" tab of your user new IAM user. 
2. Click on "Create access key" tab. 
3. Click on "Other" for the "Use case". 
4. Click on "Next" and fill out the "Description tag value" (name the secret). 
5. Click on "Create access key". 
6. Make sure to copy the Access Key ID and Secret Access Key. 
   - You will need these for your GitHub Actions Workflows.
   - Store these credentials securely, as you will not be able to view the Secret Access Key again. 🔒
   - You can also download the credentials as a CSV file for safekeeping.
7. Click "Done" to finish. 🎉

## 📄 Create IAM Policy
To create an IAM policy that grants the necessary permissions for the GitHub Actions workflows, follow these steps:
1. Create the `<Project>_speakeasy_github_actions_policy` Policy:
- In the IAM console, go to "Policies" and click "Create policy".
- Switch to the "JSON" tab and paste the following policy:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "iam:CreateRole",
                "iam:DeleteRole",
                "iam:DeleteRolePolicy",
                "iam:GetRole",
                "iam:GetRolePolicy",
                "iam:PassRole",
                "iam:PutRolePolicy",
                "iam:TagPolicy",
                "iam:TagRole",
                "iam:UntagPolicy",
                "iam:UntagRole"
            ],
            "Resource": [
                "arn:aws:iam::<AWSAccountId>:role/<Project>-speakeasy-lambda-execution-iam-role-beta",
                "arn:aws:iam::<AWSAccountId>:role/<Project>-speakeasy-lambda-execution-iam-role-prod",
                "arn:aws:iam::<AWSAccountId>:role/<Project>-speakeasy-step-functions-iam-role-beta",
                "arn:aws:iam::<AWSAccountId>:role/<Project>-speakeasy-step-functions-iam-role-prod"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:CreateBucket",
                "s3:DeleteBucket",
                "s3:GetBucketNotification",
                "s3:GetBucketTagging",
                "s3:GetLifecycleConfiguration",
                "s3:GetObject",
                "s3:PutBucketNotification",
                "s3:PutBucketTagging",
                "s3:PutLifecycleConfiguration",
                "s3:PutObject",
                "s3:GetBucketLocation"
            ],
            "Resource": [
                "arn:aws:s3:::<Project>-lambdas",
                "arn:aws:s3:::<Project>-lambdas/*",
                "arn:aws:s3:::<Project>-speakeasy-2025-beta",
                "arn:aws:s3:::<Project>-speakeasy-2025-beta/*",
                "arn:aws:s3:::<Project>-speakeasy-2025-prod",
                "arn:aws:s3:::<Project>-speakeasy-2025-prod/*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:ListAllMyBuckets",
                "s3:ListBucket"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "cloudformation:CreateStack",
                "cloudformation:UpdateStack",
                "cloudformation:DeleteStack",
                "cloudformation:DescribeStacks",
                "cloudformation:DescribeStackResources",
                "cloudformation:ListStackResources",
                "cloudformation:CreateChangeSet",
                "cloudformation:DeleteChangeSet",
                "cloudformation:DescribeChangeSet",
                "cloudformation:ListChangeSets",
                "cloudformation:ExecuteChangeSet",
                "cloudformation:GetTemplate",
                "cloudformation:GetTemplateSummary",
                "cloudformation:TagResource",
                "cloudformation:UntagResource"
            ],
            "Resource": [
                "arn:aws:cloudformation:us-east-1:<AWSAccountId>:stack/<Project>-speakeasy*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "cloudformation:ListStacks",
                "cloudformation:ValidateTemplate"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "transcribe:GetTranscriptionJob",
                "transcribe:StartTranscriptionJob"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "translate:TranslateText"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "polly:SynthesizeSpeech"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "lambda:AddPermission",
                "lambda:CreateFunction",
                "lambda:DeleteFunction",
                "lambda:GetFunction",
                "lambda:InvokeFunction",
                "lambda:RemovePermission",
                "lambda:TagResource",
                "lambda:UntagResource"
            ],
            "Resource": [
                "arn:aws:lambda:us-east-1:<AWSAccountId>:function:<Project>-speakeasy-trigger-beta",
                "arn:aws:lambda:us-east-1:<AWSAccountId>:function:<Project>-speakeasy-trigger-prod",
                "arn:aws:lambda:us-east-1:<AWSAccountId>:function:<Project>-speakeasy-transcribe-beta",
                "arn:aws:lambda:us-east-1:<AWSAccountId>:function:<Project>-speakeasy-transcribe-prod",
                "arn:aws:lambda:us-east-1:<AWSAccountId>:function:<Project>-speakeasy-translate-beta",
                "arn:aws:lambda:us-east-1:<AWSAccountId>:function:<Project>-speakeasy-translate-prod",
                "arn:aws:lambda:us-east-1:<AWSAccountId>:function:<Project>-speakeasy-synthesize-beta",
                "arn:aws:lambda:us-east-1:<AWSAccountId>:function:<Project>-speakeasy-synthesize-prod",
                "arn:aws:lambda:us-east-1:<AWSAccountId>:function:<Project>-speakeasy-transcription-status-beta",
                "arn:aws:lambda:us-east-1:<AWSAccountId>:function:<Project>-speakeasy-transcription-status-prod",
                "arn:aws:lambda:us-east-1:<AWSAccountId>:function:<Project>-speakeasy-translation-status-beta",
                "arn:aws:lambda:us-east-1:<AWSAccountId>:function:<Project>-speakeasy-translation-status-prod",
                "arn:aws:lambda:us-east-1:<AWSAccountId>:function:<Project>-speakeasy-synthesis-status-beta",
                "arn:aws:lambda:us-east-1:<AWSAccountId>:function:<Project>-speakeasy-synthesis-status-prod"
            ]
        },
        {
            "Effect": "Allow",
            "Action": "lambda:ListFunctions",
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "states:CreateActivity",
                "states:CreateStateMachine",
                "states:DeleteActivity",
                "states:DeleteStateMachine",
                "states:DescribeActivity",
                "states:DescribeExecution",
                "states:DescribeStateMachine",
                "states:GetActivityTask",
                "states:GetExecutionHistory",
                "states:StartExecution",
                "states:StopExecution",
                "states:SendTaskFailure",
                "states:SendTaskSuccess",
                "states:TagResource",
                "states:UntagResource",
                "states:UpdateStateMachine"
            ],
            "Resource": [
                "arn:aws:states:us-east-1:<AWSAccountId>:stateMachine:<Project>-speakeasy-audio-processing-state-machine-beta",
                "arn:aws:states:us-east-1:<AWSAccountId>:stateMachine:<Project>-speakeasy-audio-processing-state-machine-prod"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "states:ListActivities",
                "states:ListExecutions",
                "states:ListStateMachines"
            ],
            "Resource": "*"
        }
    ]
}
```
- Set the `AWSAccountId` to your AWS account ID.
- Change the region in the ARNs if you are not using `us-east-1`.
- Change the IAM role names to `your` IAM roles names.
- Change the Lambda function names to `your` functions names.
- Change the cloudformation stack names to `your` stack names.
- Change the S3 bucket names to `your` bucket names.
- Change the state machine names to `your` state machine names.
- Click on "Review policy".
- Click "Next" and give it a name `<Project>_speakeasy_github_actions_policy`.
- Click on "Create policy" to save it. 📝

2. Attach the Policy to the User:
   - Go back to the IAM user you created earlier e.g. `<Project>_speakeasy_github_actions_user`.
   - Click on the "Permissions" tab, then click "Add permissions".
   - Choose "Attach existing policies directly", search for `<Project>_speakeasy_github_actions_policy`, select it.
   - Click "Next" and then "Add permissions" to attach the policy to the user. ➕

## 🔐 Configure GitHub Secrets
To configure GitHub Secrets for your repository, follow these steps:
1. Go to your GitHub repository.
2. Navigate to `Settings` > `Environments`.
3. Create two environments:
   - `beta`
   - `prod`
   1. Click on "New environment" button.
   2. Name the environment `beta` and click "Configure environment" button.
   3. Repeat the same steps to create the `prod` environment.
4. Add secrets to the environments:
   1. Click on the "Environments" button on the left sidebar.
   2. Select the `beta` environment.
      1. Click on the "Add environment secret" button.
      2. Add the following secret:
         - S3_BUCKET_AUDIO
      3. Enter the corresponding value for the secret:
            - Your S3 bucket name for audio files (e.g., `<Project>-speakeasy-2025-beta`).
      4. Click on "Add secret" button to save the secret.
   3. Repeat the same steps for the `prod` environment:
      1. Click on the "Add environment secret" button.
      2. Add the following secret:
         - S3_BUCKET_AUDIO
      3. Enter the corresponding value for the secret:
            - Your S3 bucket name for audio files (e.g., `<Project>-speakeasy-2025-prod`).
      4. Click on "Add secret" button to save the secret.
5. Add environment variables to the environments:
   1. Click on the "Environments" button on the left sidebar.
   2. Select the `beta` environment.
      1. Click on the "Add environment variable" button.
      2. Add the following environment variable:
         - LAMBDA_TRIGGER
      3. Enter the corresponding value for the environment variable:
            - `<Project>-speakeasy-trigger-beta`
      4. Click on "Add variable" button to save the variable.
   3. Repeat the same steps for the `prod` environment:
      1. Click on the "Add environment variable" button.
      2. Add the following environment variable:
         - LAMBDA_TRIGGER
      3. Enter the corresponding value for the environment variable:
            - `<Project>-speakeasy-trigger-prod`
      4. Click on "Add variable" button to save the variable.
6. Add the following repository secrets:
   1. Go to your GitHub repository.
   2. Navigate to `Settings` > `Secrets and variables` > `Actions`.
   3. Click on "New repository secret" button.
   4. Add the following secrets:
      1. Name the secrets as follows:
         - AWS_ACCESS_KEY_ID
         - AWS_REGION 
         - AWS_SECRET_ACCESS_KEY
         - S3_BUCKET_LAMBDAS
      2. Enter the corresponding values for each secret:
         - For example:
           - AWS_ACCESS_KEY_ID: Your IAM user's access key ID.
           - AWS_REGION: The AWS region where your resources are deployed (e.g., `us-east-1`).
           - AWS_SECRET_ACCESS_KEY: Your IAM user's secret access key.
           - S3_BUCKET_LAMBDAS: Your S3 bucket name for Lambda function packages (e.g., `<Project>-lambdas`).
      3. Click "Add secret" button to save each secret. 💾
7. Add the following repository variables:
   1. Go to your GitHub repository.
   2. Navigate to `Settings` > `Secrets and variables` > `Actions`.
   3. Click on the "Variables" tab.
   4. Click on "New repository variable" button.
   5. Add the following variables:
      1. Name the variables as follows:
         - APP_NAME
         - STACK_NAME
      2. Enter the corresponding values for each variable:
         - For example:
           - APP_NAME: Your application name (e.g., `speakeasy`).
           - STACK_NAME: Your CloudFormation stack name (e.g., `<Project>-speakeasy`).
      3. Click "Add variable" button to save each variable. 📝

## 🔧 Modify Configuration Files
To modify the configuration files, follow these steps:
1. Update *template.yaml*
- Modify the following parameters to `your` values:
```yaml
  LambdaCodeS3BucketName:
    Type: String
    Default: <Project>-lambdas
    Description: The S3 bucket where Lambda function code is stored

  AudioS3BucketName:
    Type: String
    Default: <Project>-speakeasy-2025
    Description: The name of the audio S3 bucket

  TriggerLambdaName:
    Type: String
    Default: <Project>-speakeasy-trigger
    Description: The name of the Upload Trigger Lambda function

  TranscribeLambdaName:
    Type: String
    Default: <Project>-speakeasy-transcribe
    Description: The name of the Transcribe Lambda function

  TranscriptionStatusLambdaName:
    Type: String
    Default: <Project>-speakeasy-transcription-status
    Description: The name of the Transcribe Status Lambda function

  TranslateLambdaName:
    Type: String
    Default: <Project>-speakeasy-translate
    Description: The name of the Translate Lambda function

  TranslationStatusLambdaName:
    Type: String
    Default: <Project>-speakeasy-translation-status
    Description: The name of the Translate Status Lambda function

  SynthesizeLambdaName:
    Type: String
    Default: <Project>-speakeasy-synthesize
    Description: The name of the Synthesize Lambda function

  SynthesisStatusLambdaName:
    Type: String
    Default: <Project>-speakeasy-synthesis-status
    Description: The name of the Synthesize Status Lambda function

  TriggerLambdaS3Key:
    Type: String
    Default: speakeasy/trigger.zip
    Description: The prefix for the Upload Trigger Lambda function code files in the S3 bucket

  TranscribeLambdaS3Key:
    Type: String
    Default: speakeasy/transcribe.zip
    Description: The prefix for the Lambda function code files in the S3 bucket

  TranscriptionStatusLambdaS3Key:
    Type: String
    Default: speakeasy/status_transcription.zip
    Description: The prefix for the Lambda function code files in the S3 bucket

  TranslateLambdaS3Key:
    Type: String
    Default: speakeasy/translate.zip
    Description: The prefix for the Lambda function code files in the S3 bucket

  TranslationStatusLambdaS3Key:
    Type: String
    Default: speakeasy/status_translation.zip
    Description: The prefix for the Lambda function code files in the S3 bucket

  SynthesizeLambdaS3Key:
    Type: String
    Default: speakeasy/synthesize.zip
    Description: The prefix for the Lambda function code files in the S3 bucket

  SynthesisStatusLambdaS3Key:
    Type: String
    Default: speakeasy/status_synthesis.zip
    Description: The prefix for the Lambda function code files in the S3 bucket

  AudioProcessingStateMachineName:
    Type: String
    Default: <Project>-speakeasy-audio-processing-state-machine
    Description: The name of the Audio Processing Step Functions state machine

  StepFunctionsIAMRoleName:
    Type: String
    Default: <Project>-speakeasy-step-functions-iam-role
    Description: The name of the Step Functions IAM role

  LambdaExecutionIAMRoleName:
    Type: String
    Default: <Project>-speakeasy-lambda-execution-iam-role
    Description: The name of the Lambda Execution IAM role

  TriggerLambdaHandler:
    Type: String
    Default: trigger.lambda_handler
    Description: The handler for the Upload Trigger Lambda function

  TranscribeLambdaHandler:
    Type: String
    Default: transcribe.lambda_handler
    Description: The handler for the Transcribe Lambda function

  TranscriptionStatusLambdaHandler:
    Type: String
    Default: status_transcription.lambda_handler
    Description: The handler for the Transcription Status Lambda function

  TranslateLambdaHandler:
    Type: String
    Default: translate.lambda_handler
    Description: The handler for the Translate Lambda function

  TranslationStatusLambdaHandler:
    Type: String
    Default: status_translation.lambda_handler
    Description: The handler for the Translate Status Lambda function

  SynthesizeLambdaHandler:
    Type: String
    Default: synthesize.lambda_handler
    Description: The handler for the Synthesize Lambda function

  SynthesisStatusLambdaHandler:
    Type: String
    Default: status_synthesis.lambda_handler
    Description: The handler for the Synthesize Status Lambda function

  OwnerNameTag:
    Type: String
    Default: "Cloud DevOps Engineering"
    Description: The department responsible for the resource.

  ApplicationNameTag:
    Type: String
    Default: "<Project> SpeakEasy"
    Description: The name of the application.

  VersionTag:
    Type: String
    Default: "1.0"
    Description: The version of the application.

  LifecycleStatusTag:
    Type: String
    Default: Active
    Description: The lifecycle status of the resource (e.g., Active, Deprecated, Archived).

  AutomationDetailsTag:
    Type: String
    Default: "Created by AWS CloudFormation"
    Description: Details about the automation process that created the resource.

  CreatedOnTag:
    Type: String
    Default: "2025-07-23"
    Description: The date when the resource was created, in YYYY-MM-DD format.
```

## 📦 GitHub Repository Structure
The structure of the GitHub repository is as follows:
```angular2html
├── .github
│   ├── pull_request_template.md
│   └── workflows
│       ├── deploy.yaml
│       ├── destroy.yaml
│       └── upload_audio.yaml
├── audio_inputs
│   └── marvin.mp3
├── cloudformation
│   └── template.yaml
├── lambda
│   ├── status_synthesis.py
│   ├── status_transcription.py
│   ├── status_translation.py
│   ├── synthesize.py
│   ├── transcribe.py
│   ├── translate.py
│   ├── trigger.py
│   └── helpers
│       ├── datetime_serializer.py
│       └── logger.py
├── .gitignore
├── LICENSE
└── README.md
```

## 🔀 Create beta Branch
We need to have the beta branch for our workflow to work properly. This branch will be used for beta testing and development. Follow these steps to create the `beta` branch:
1. Create a new branch named `beta` from the `main` branch.
   - This branch will be used for beta testing and development.
   - You can create the branch using the following command:
     ```bash
     git checkout -b beta
     ```
2. Push the `beta` branch to the remote repository:
   ```bash
   git push origin beta
   ```
3. Advise to use your own branch for development & testing, and then merge it into the `beta` branch when ready to test.
4. Once the beta testing is complete, merge the `beta` branch into the `main` branch to deploy the changes to production.

## 🚀 Deploy Resources
To deploy the resources, you can use the GitHub Actions workflows provided in the `.github/workflows` directory.
1. **Deploy Beta**: This workflow will deploy the CloudFormation stack and create the necessary resources.
   1. Goto Actions tab in your GitHub repository.
   2. Select the `Deploy Resources` workflow on the left sidebar.
   3. Click on the "Run workflow" button on the right side.
   4. Select the branch you want to deploy from (use, `beta`).
   5. Select the action you want to perform (use, `Deploy`).
   6. Select the environment you want to deploy to (use, `beta`).
   7. Click on the "Run workflow" button to start the deployment.
2. **Deploy Prod**: This workflow will deploy the CloudFormation stack and create the necessary resources for production.
   1. Goto Actions tab in your GitHub repository.
   2. Select the `Deploy Resources` workflow on the left sidebar.
   3. Click on the "Run workflow" button on the right side.
   4. Select the branch you want to deploy from (use, `main`).
   5. Select the action you want to perform (use, `Deploy`).
   6. Select the environment you want to deploy to (use, `main`).
   7. Click on the "Run workflow" button to start the deployment.

## 💣 Destroy Resources
To destroy the resources created by the CloudFormation stack, you can use the GitHub Actions workflows provided in the `.github/workflows` directory.
1. **Destroy Beta**: This workflow will destroy the CloudFormation stack and delete the resources created in the beta environment.
   1. Goto Actions tab in your GitHub repository.
   2. Select the `Destroy Resources` workflow on the left sidebar.
   3. Click on the "Run workflow" button on the right side.
   4. Select the branch you want to deploy from (use, `beta`).
   5. Select the action you want to perform (use, `Destroy`).
   6. Select the environment you want to deploy to (use, `beta`).
   7. Click on the "Run workflow" button to start the destruction process.
2. **Destroy Prod**: This workflow will destroy the CloudFormation stack and delete the resources created in the production environment.
   1. Goto Actions tab in your GitHub repository.
   2. Select the `Destroy Resources` workflow on the left sidebar.
   3. Click on the "Run workflow" button on the right side.
   4. Select the branch you want to deploy from (use, `main`).
   5. Select the action you want to perform (use, `Destroy`).
   6. Select the environment you want to deploy to (use, `maim`).
   7. Click on the "Run workflow" button to start the destruction process.

## 🚧 Update Resources
**☠️ USE AT YOUR OWN RISK! ☠️**
To update the resources created by the CloudFormation stack, you can use the GitHub Actions workflows provided in the `.github/workflows` directory.
1. **Update Beta**: This workflow will update the CloudFormation stack and apply the changes made in the `beta` branch.
   1. Goto Actions tab in your GitHub repository.
   2. Select the `Deploy Resources` workflow on the left sidebar.
   3. Click on the "Run workflow" button on the right side.
   4. Select the branch you want to deploy from (use, `beta`).
   5. Select the action you want to perform (use, `Update`).
   6. Select the environment you want to deploy to (use, `beta`).
   7. Click on the "Run workflow" button to start the update process.
2. **Update Prod**: This workflow will update the CloudFormation stack and apply the changes made in the `main` branch.
   1. Goto Actions tab in your GitHub repository.
   2. Select the `Deploy Resources` workflow on the left sidebar. 
   3. Click on the "Run workflow" button on the right side. 
   4. Select the branch you want to deploy from (use, `main`). 
   5. Select the action you want to perform (use, `Update`). 
   6. Select the environment you want to deploy to (use, `main`). 
   7. Click on the "Run workflow" button to start the update process.

## 🔄 Trigger Audio Processing
To trigger the workflows, upload mp3's to the `audio_inputs/` directory in your repository.
1. Push request to either `beta` or `main` branch will trigger the `Upload Audio` workflow.
2. Strategy to maintain the workflow:
   - Create a new branch for your changes.
   - Add files to the `audio_inputs` directory in your repository.
   - Create a pull request to merge your changes into the `beta` branch.
   - The workflow will automatically upload the audio files to the `S3_BUCKET_AUDIO` secret under the `audio_inputs` prefix.
     - Newly created audio files in the `audio_inputs/` prefix will trigger an S3 event notification.
     - The S3 event notification will invoke the `trigger.py` lambda function which in turn will start the Step Functions state machine to process the audio files.
     - The state machine will invoke the Lambda functions to transcribe, translate, and synthesize the audio files.
     - The results will be stored in the S3 bucket specified in the `S3_BUCKET_AUDIO` secret under the `transcriptions`, `translations`, and `audio_outputs` prefixes respectively.
   - Once beta testing is complete, merge the `beta` branch into the `main` branch to process the `audio_inputs/` in production.

## 🏁 Conclusion
This project is designed to help you transcribe, translate, and synthesize audio files using AWS services and GitHub Actions. By following the steps outlined above, you can set up your environment and deploy the necessary resources to get started.

Ensure that your AWS credentials are kept secure and not shared publicly. 🔒