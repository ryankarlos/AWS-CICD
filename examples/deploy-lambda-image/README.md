# Deploy Tweepy Streaming App Code to Lambda Image 
The code pipeline workflow is represented diagramatically for this use case. We will be deploying an application container to lambda which streams tweets 
about a topic for a chosen duration.The updates to required roles and deployment of Lambda Image resource is automated using CloudFormation templates.
In the intended workflow, the user commits to CodeCommit which triggers codepipeline execution via EventBridge. This executes Source Stage (which fetches
cloud formation templates from S3), Build Stage (builds application code and pushes to ECR), Deploy Stage (which deploys to Lambda container resource) and finally runs end to end test on the deployed code to check it executes/functions as expected.

<img src="https://github.com/ryankarlos/AWS-CICD/blob/master/screenshots/architecture_tweets_deploy_lambda-container.png"></img>

## Running local script

* Need to install click https://click.palletsprojects.com/en/8.1.x/quickstart/ in virtual environment
The command and argument options can be viewed in cli by running command below 
  
```
$ python local_run.py --help 
                                             
Usage: local_run.py [OPTIONS] KEYWORD

  function for checking/testing tweepy streaming and search api locally before
  deploying as lambda image container For 'realtime' delivery - may need to
  use a trending topic as 'keyword' otherwise will have to wait a while to get
  anything. Multiple calls in short time window to streaming api may invoke
  420 error. If test import speed option is set as True, the import stats will
  be reported before the script ends

Options:
  --delivery [search|realtime]  mode of delivery, using search api or realtime
                                streaming api
  --duration INTEGER            How long (secs) to let stream run before
                                disconnecting
  --test_import_speeds BOOLEAN  Uses line profiler to test speed of imports of
                                custom util functions
  --help                        Show this message and exit.
```

* Passing only keyword and leaving other option args as defaults


```
python local_run.py 'machine learning' 
```
* Or passing in options as well. The output also include profiling for imports of packages

```
python local_run.py 'machine learning'  --delivery search --duration 10 --test_import_speeds True

Successfully retrieved aws secrets !
Starting search stream using tweepy Twitter API v1.1 Client: 

{'created_at': datetime.datetime(2022, 4, 10, 4, 42, 31, tzinfo=datetime.timezone.utc), 'handle': 'maggie_albrecht', 'text': 'I just answered today\'s machine learning question on @0xbnomial!\n\n"Peter needs a better balance"\n\nSo far, people ha… https://t.co/oICenX3HeK', 'favourite_count': 42393, 'retweet_count': 0, 'retweeted': False, 'followers_count': 2028, 'friends_count': 4997, 'location': '', 'lang': None}
{'created_at': datetime.datetime(2022, 4, 10, 4, 41, 22, tzinfo=datetime.timezone.utc), 'handle': 'machinelearnflx', 'text': 'Machine Learning de A-Z https://t.co/ukkYh7aKMY  #machinelearning #datascience #bigdata #AI #learning #elearning #ad', 'favourite_count': 205, 'retweet_count': 1, 'retweeted': False, 'followers_count': 123991, 'friends_count': 36005, 'location': '', 'lang': None}
{'created_at': datetime.datetime(2022, 4, 10, 4, 39, 39, tzinfo=datetime.timezone.utc), 'handle': 'Schlemielforeal', 'text': 'Some of these Machine Learning Memes are frankly unassailable. https://t.co/jjvBvR6upE', 'favourite_count': 3644, 'retweet_count': 0, 'retweeted': False, 'followers_count': 100, 'friends_count': 568, 'location': 'The Darkest Timeline', 'lang': None}
............
............
............
{'created_at': datetime.datetime(2022, 4, 9, 22, 38, 3, tzinfo=datetime.timezone.utc), 'handle': 'ThePostsynaptic', 'text': 'A robust and interpretable machine learning approach using multimodal biological data to predict future pathologica… https://t.co/wf60yZuxYH', 'favourite_count': 50, 'retweet_count': 0, 'retweeted': False, 'followers_count': 2823, 'friends_count': 4861, 'location': 'UK and many places', 'lang': None}
{'created_at': datetime.datetime(2022, 4, 9, 22, 37, 48, tzinfo=datetime.timezone.utc), 'handle': 'CandleJackie', 'text': '@Sessler Also upsetting: learning that the machine being raged against was not the crappy microwave in the break room.', 'favourite_count': 28, 'retweet_count': 0, 'retweeted': False, 'followers_count': 10, 'friends_count': 0, 'location': 'France', 'lang': None}
{'created_at': datetime.datetime(2022, 4, 9, 22, 37, 3, tzinfo=datetime.timezone.utc), 'handle': 'milocamj', 'text': 'How Ai And Machine Learning Are Impacting B2b Companies? – https://t.co/Sg4crIw0aM - ICTSD Bridges News… https://t.co/Z23xDgATtB', 'favourite_count': 3952, 'retweet_count': 0, 'retweeted': False, 'followers_count': 2645, 'friends_count': 49, 'location': 'Miami, FL', 'lang': None}

 10 seconds time limit reached, so disconneting stream
 323 tweets streamed ! 

Timer unit: 1e-06 s

Total time: 0.612584 s
File: /Users/rk1103/Documents/codecommit_dockerbuild/local_run.py
Function: profiled_function at line 7

Line #      Hits         Time  Per Hit   % Time  Line Contents
==============================================================
     7                                           def profiled_function():
     8         1     403236.0 403236.0     65.8      from secrets import get_secrets
     9         1     209346.0 209346.0     34.2      from tweets_api import MyStreamListener
    10         1          2.0      2.0      0.0      from tweets_api import tweepy_search_api
```

### Creating source repo, roles, artifacts and code pipeline

Setup codecommit repo as detailed in main `README.md` to contain all the code in this folder `deploy-lambda-image`

The cf templates folder contains the roles resources and deployment resource configs. We will need to create 
these stacks with cloudformation before they are used within the pipeline for stack updates
https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-cli-creating-stack.html

```
$ aws cloudformation create-stack --stack-name CodeDeployLambdaTweets --template-body file://cf-templates/CodeDeployLambdaTweepy.yaml

$ aws cloudformation create-stack --stack-name RoleCloudFormationforCodeDeploy --template-body file://cf-templates/roles/CloudFormationRole.yaml

$ aws cloudformation create-stack --stack-name RoleCodePipeline --template-body file://cf-templates/roles/CodepipelineRole.yaml

$ aws cloudformation create-stack --stack-name RoleLambdaImage --template-body file://cf-templates/roles/RoleLambdaImageStaging.yaml
```

Zip the cf templates folder in main repo, not included in the application code `deploy-lambda-image` source repo. 
This is required for the Deploy stage in codepipeline and needs to be read in the source stage and output as artifacts.
We will copy this zipped folder to S3 and configure code pipeline in defintion file so that action in source stage 
reads from the s3 location of template file

```
$ cd cf-templates 
$ zip template-source-artifacts.zip CodeDeployLambdaTweepy.yaml roles/*

  adding: CodeDeployLambdaTweepy.yaml (deflated 42%)
  adding: roles/CloudFormationRole.yaml (deflated 59%)
  adding: roles/CodepipelineRole.yaml (deflated 79%)
  adding: roles/RoleLambdaImageStaging.yaml (deflated 58%)
  
$ aws s3 cp template-source-artifacts.zip s3://codepipeline-us-east-1-49345350114/lambda-image-deploy/template-source-artifacts.zip

upload: ./template-source-artifacts.zip to s3://codepipeline-us-east-1-49345350114/lambda-image-deploy/template-source-artifacts.zip
```

Then create codepipeline from the definition json file in `codepipeline_definitions/deploy-lambda-image.json` using 
the command below (assuming run from the root of this repo) https://docs.aws.amazon.com/codepipeline/latest/userguide/pipelines-create.html
The definition json assumes code pipeline role is created before and 

```
$ aws codepipeline create-pipeline --cli-input-json file://cp-definitions/deploy-lambda-image.json
```

This should create the pipeline which should be visible in the console or via cli `list-pipelines` 

```
aws codepipeline list-pipelines
{
    "pipelines": [
        {
            "name": "lambda-image-deploy",
            "version": 30,
            "created": "2022-05-30T03:11:28.501000+01:00",
            "updated": "2022-06-02T00:19:21.596000+01:00"
        }
    ]
}

```


## Triggering code pipeline 

Once the pipeline has been created above, it will automatically execute

<img width="1000" src="https://github.com/ryankarlos/codepipeline/blob/master/screenshots/TweetsLambdaDeploy-pipelineviz-1.png">

<img width="1000" src="https://github.com/ryankarlos/codepipeline/blob/master/screenshots/TweetsLambdaDeploy-pipelineviz-2.png">

Code Pipeline has been configured to trigger with every push to CodeCommit via EventBridge. This will
start the source stage, transition to build phase if successful where the commands in buildspec.yml  will be executed 
in different phases of build process
https://docs.aws.amazon.com/codebuild/latest/userguide/getting-started-cli-create-build-spec.html
Finally it will transition to Deploy and TestInvocation Stages if successful (as in diagram above). 

CodePipeline will also trigger automatically if the source artifact zip in S3 is updated. 

For manual triggering, choose Release change on the pipeline details page on the console. This runs the most recent 
revision available in each source location specified in a source action through the pipeline.

<img width="1000" src="https://github.com/ryankarlos/codepipeline/blob/master/screenshots/codepipeline_executionhistory.png">

Once the pipeline has finished, we can check CloudWatch to see the invocation logs in the corresponding log stream

<img width="1000" src="https://github.com/ryankarlos/codepipeline/blob/master/screenshots/lambda_invocation_logs.png">

## Optional: Manual Method of Lambda Image Deployment and Execution via cli

CodePipeline already automates these steps. However, for more control over creating and invoking the function, 
we can do this manually via the cli (assuming ECR URI has the build we need)

To create a new function - you can either do it via console or follow the cli command here.
You would need to create a new role and  grant permissions to lambda to performa actions to other
services e.g. logs to cloudwatch, access data from S3 etc (see iam_permissions folder)

https://docs.aws.amazon.com/cli/latest/reference/lambda/create-function.html

For this case, Ive increased the memory size from default 128MB to 1024MB as was running into memory issues 
when streaming causing execution to error.
Also default timeout is 3 secs, which has been overriden to 5 mins. 
Execution may finish before depending on what the duration parameter is set to payload

```
aws lambda create-function --region us-east-1 --function-name my-function --package-type Image --code ImageUri=<ECR Image URI> --role <arn-role> ----memory-size 1024 --timeout 300
```

To invoke the function, first fetch the arn. If you can't remember, execute following command via cli
and fetch value of  "FunctionArn"

```
$ aws lambda list-functions 
```

Then run following command listed in https://docs.aws.amazon.com/cli/latest/reference/lambda/invoke.html
This includes payload, arn which was just accessed and json output file to store the response. 

```
$ aws lambda invoke --function-name <lambda-arn> --payload '{ "keyword": "machine learning", "delivery": "search", "duration": 15 }' --cli-binary-format 'raw-in-base64-out'  outfile.json 

{
    "StatusCode": 200,
    "FunctionError": "Unhandled",
    "ExecutedVersion": "$LATEST"
}
```

Note that, ive set the --cli-binary-format parameter to raw-in-base64-out. Otherwise, i got the following error below.
On google searching, i found this useful blog diagnosing the error https://bobbyhadz.com/blog/aws-cli-invalid-base64-lambda-error
Seems by setting the --cli-binary-format parameter to raw-in-base64-out  a raw JSON string can be passed to the --payload parameter, 
otherwise it expects a base-64-encoded input

```
Invalid base64: "{"keyword": "machine learning", "delivery": "search", "duration": 15}"
```

For subsequent builds, the existing function config would need to be updated to using
the latest docker image


```
$ aws lambda update-function-code --function-name LambdaTwitter --image-uri <image-uri>

{
    "FunctionName": "LambdaTwitter",
    "FunctionArn": "<functiom-arn>",
    "Role": "<role-arn>",
    "CodeSize": 0,
    "Description": "",
    "Timeout": 300,
    "MemorySize": 1024,
    "LastModified": "2022-04-18T04:27:04.000+0000",
    "CodeSha256": "4682f2366dd01d79d8696de41d91bc85c286e5905018727f43c7dd7935002d62",
    "Version": "$LATEST",
    "TracingConfig": {
        "Mode": "PassThrough"
    },
    "RevisionId": "66472954-e2ef-4461-b582-86d79a190da7",
    "State": "Active",
    "LastUpdateStatus": "InProgress",
    "LastUpdateStatusReason": "The function is being created.",
    "LastUpdateStatusReasonCode": "Creating",
    "PackageType": "Image",
    "ImageConfigResponse": {}
}

```
