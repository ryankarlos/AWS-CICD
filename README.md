# AWS Codepipeline Demo
Demo of using code pipeline to build docker container and running with lambda function invocation  
This application is using tweepy for streaming tweets 


## Setting up ssh (note to self)

Currently configured to push to both code commit and github repos when 
runnin `git push origin master`

```
$ git remote -v
origin	ssh://git-codecommit.us-east-1.amazonaws.com/v1/repos/codecommit_dockerbuild (fetch)
origin	git@github.com:ryankarlos/codepipeline.git (push)
origin	ssh://git-codecommit.us-east-1.amazonaws.com/v1/repos/codecommit_dockerbuild (push)
```

May need to run the following to add ssh key if get `Permission denied (publickey)` error when
trying to push to remote

```
ssh-add --apple-use-keychain ~/.ssh/codecommit_rsa
```

#### Running local script

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

#### Triggering code pipeline and building docker image

<img width="1000" alt="screnshots/codepipeline_executionhistory" src="https://github.com/ryankarlos/codepipeline/blob/master/screenshots/codepipeline_stages.png">


Code Pipeline has been configured to trigger with every push to github/code commit repo. This will
start the build phase, which runs the commands in buildspec.yml in different phases of build process
https://docs.aws.amazon.com/codebuild/latest/userguide/getting-started-cli-create-build-spec.html

Environment variables are defined and new roles defined when creating code build stage.
https://docs.aws.amazon.com/codebuild/latest/userguide/sample-docker.html

<img width="1000" alt="screnshots/codepipeline_executionhistory" src="https://github.com/ryankarlos/codepipeline/blob/master/screenshots/codepipeline_executionhistory.png">


#### Setting up and in invoking lambda function to execute code in container

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
<img width="1000" alt="cloudwatch_lambda_executions" src="https://github.com/ryankarlos/codepipeline/blob/master/screenshots/cloudwatch_lambda_executions.png">


Note that, ive set the --cli-binary-format parameter to raw-in-base64-out. Otherwise, i got the following error below.
On google searching, i found this useful blog diagnosing the error https://bobbyhadz.com/blog/aws-cli-invalid-base64-lambda-error
Seems by setting the --cli-binary-format parameter to raw-in-base64-out  a raw JSON string can be passed to the --payload parameter, 
otherwise it expects a base-64-encoded input

```
Invalid base64: "{"keyword": "machine learning", "delivery": "search", "duration": 15}"
```
