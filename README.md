# codepipeline
Demo of using code pipeline to build docker container and running with lambda function invocation  
This application is using tweepy for streaming tweets 

#### Running local script



#### Triggering code pipeline and building docker image



#### Setting up and in invoking lambda function to execute code in container

To create a new function - you can either do it via console or follow the cli command here.
You would need to create a new role and  grant permissions to lambda to performa actions to other
services e.g. logs to cloudwatch, access data from S3 etc

https://docs.aws.amazon.com/cli/latest/reference/lambda/create-function.html

```
aws lambda create-function --region us-east-1 --function-name my-function --package-type Image --code ImageUri=<ECR Image URI> --role <arn-role> 
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
