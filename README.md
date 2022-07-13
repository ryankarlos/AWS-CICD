## AWS CodePipeline 

Here we will demonstate an examples of setting up CI-CD pipelines using AWS code pipeline for software delivery automation. Using CodeCommit, 
CodeBuild and CodeDeploy for versioning, building, testing and deploying applications in the cloud.
We will configure AWS CodePipeline to build an ECR image and deploy the latest version to lambda container.
The application code will stream tweets using tweepy library to kinesis stream.
First we need to setup codepipeline and he various stages before invoking our lambda to stream tweets. Once this is complete, 
navigate to this [page](examples/deploy-lambda-image) to setup kinesis stream resource and stream tweets to it.

### Setting up Code Pipeline 


Typically a codepipeline job contains the following stages but could be fewer or more
depending on the application for e.g. could have more envs for testing before deplopyoing to 
prod. Please refer to the references section for more information in the links provided.


* **Source**
In this step the latest version of our source code will be fetched from our repository and uploaded to an S3 bucket.
The application source code is maintained in a repository configured as a GitHub source action in the pipeline. 
When developers push commits to the repository, CodePipeline detects the pushed change, and a pipeline execution 
starts from the Source Stage. The GitHub source action completes successfully (that is, the latest changes 
have been downloaded and stored to the artifact bucket unique to that execution). The output artifacts 
produced by the GitHub source action, which are the application files from the repository, are then used as 
the input artifacts to be worked on by the actions in the next stage.

* **Build**
During the build step we will use this uploaded source code and automate our manual packaging step using a CodeBuild project.
The build task pulls a build environment image and builds the application in a virtual container.

* **Unit Test**
The next action in the Prod Stage is a unit test project created in CodeBuild and configured as a test action in 
the pipeline. 

* **Deploy to Dev/Test Env**
This deploys the application to a dev/test env environment using CodeDeploy or another action 
provider such as CloudFormation.

* **Integration Test**
This runs end to end Integration testing project created in CodeBuild and configured as a test action in the pipeline.

* **Deploy to ProdEnv**
This deploys the application to a production environment. Could configure the pipeline so this stage
requires manual approval to execute

### Setting up Source Stage


#### CodeCommit 
This assumes using ssh keys and on mac-os. If not setup ssh keys already using `ssh-keygen` as in
[docs](https://docs.aws.amazon.com/codecommit/latest/userguide/setting-up-ssh-unixes.html)
Upload your SSH public key to your IAM user. Once you have uploaded your SSH public key, copy the SSH Key ID.
Edit your SSH configuration file named "config" in your local ~/.ssh directory. 
Add the following lines to the file, where the value for User is the SSH Key ID.
```
Host git-codecommit.*.amazonaws.com
User Your-IAM-SSH-Key-ID-Here
IdentityFile ~/.ssh/Your-Private-Key-File-Name-Here
```
Once you have saved the file, make sure it has the right permissions by running the following command 
in the ~/.ssh directory:  `chmod 600 config`

Create a new code commit as in repo https://docs.aws.amazon.com/codecommit/latest/userguide/how-to-create-repository.html

```
aws codecommit create-repository --repository-name MyDemoRepo --repository-description "My demonstration repository" 
```

Clone your repository to your local computer and start working on code. Run the following [command](https://docs.aws.amazon.com/codecommit/latest/userguide/how-to-connect.html)
You can get the ssh uri from the console under Clone URL for the code commit repo

```
$ git clone ssh://git-codecommit.us-east-1.amazonaws.com/v1/repos/MyDemoRepo 
```


#### Optional: Configuring pushing to both CodeCommit and Github

Since code in codecommit and github cannot be automatically synced, you can configure git to push 
to both code commit and github repos when running `git push origin master`

When ssh codecommit repo to local, remote url is set automatically for 
fetch and push.

`
$ git remote -v
origin	ssh://git-codecommit.us-east-1.amazonaws.com/v1/repos/deploy-lambda-image (fetch)
origin	ssh://git-codecommit.us-east-1.amazonaws.com/v1/repos/deploy-lambda-image (push)
`

we will have to manually add an extra push-url for github repo 

`
$ git remote set-url --add --push git://another/repo.git
`

origin maps to both github and aws code commit repo urls for git push actions

```
$ git remote -v
origin	ssh://git-codecommit.us-east-1.amazonaws.com/v1/repos/codecommit_dockerbuild (fetch)
origin	git@github.com:ryankarlos/codepipeline.git (push)
origin	ssh://git-codecommit.us-east-1.amazonaws.com/v1/repos/codecommit_dockerbuild (push)
```

Note: May need to run the following to add ssh key if get `Permission denied (publickey)` error when
trying to push to remote

```
$ ssh-add --apple-use-keychain ~/.ssh/codecommit_rsa
```

#### Other Actions in Source Stage

We could also use the source stage to read in other files and output them as artifacts to be
used in downstream stages in pipeline. E.g. reading template configs zipped folder from S3 and using that as
input artifact to CloudFormation stack.


### Setting up Build Stage

First need to include a [buildspec.yml](https://docs.aws.amazon.com/codebuild/latest/userguide/getting-started-cli-create-build-spec.html)file, which CodeBuild uses to run a build.

Then you create a build project that AWS CodeBuild uses to run the build. A build project 
includes information about how to run a build, including where to get the source code, which 
build environment to use, which build commands to run, and where to store the build output.


For Operating system, choose Ubuntu.
For Runtime, choose Standard.
For Image, choose aws/codebuild/standard:4.0.

For codebuild projects involving building docker image to push to ECR, follow the [AWS doc](https://docs.aws.amazon.com/codebuild/latest/userguide/sample-docker.html)
Make sure the option, "Privileged" is ticked in build project if building docker image
Also, Important to set the following environment variables as they are referenced to
in the buildspec.yml

* AWS_DEFAULT_REGION with a value of region-ID
* AWS_ACCOUNT_ID with a value of account-ID
* IMAGE_TAG with a value of Latest
* IMAGE_REPO_NAME with a value of Amazon-ECR-repo-name


#### Optional: Checking docker image contents from ECR

For images built from CodeBuild and pushed to ECR, if you want to check contents or run docker image locally from 
Amazon ECR, you can pull it to your local environment with the docker pull command. 

First you would need to authenticate your Docker client to the Amazon ECR registry that you intend to pull your image from. 
Authentication tokens must be obtained for each registry used, and the tokens are valid for 12 hours.
The following command can be run, replacing <AWS-ACCOUNT-ID> with AWS account id.

```
$ aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <AWS-ACCOUNT-ID>.dkr.ecr.us-east-1.amazonaws.com
Login Succeeded
```

Pull the image using the docker pull command below. Add the latest tag to pull the
latest image update.

```
$ docker pull 376337229415.dkr.ecr.us-east-1.amazonaws.com/tweepy-stream-deploy:latest
Using default tag: latest
latest: Pulling from tweepy-stream-deploy
e6842361273f: Pull complete 
0a074f8b3d7a: Pull complete 
df68587c4258: Pull complete 
1418415b0a5d: Pull complete 
f2796bda02b6: Pull complete 
8c16de5f53b2: Pull complete 
849092b9d065: Pull complete 
e92895d3cb88: Pull complete 
bf7d8485ff8c: Pull complete 
4db7aa5b7411: Pull complete 
58cf742cd771: Pull complete 
Digest: sha256:29fe00678ec6cfd9f8caf36cd3bf9fae30975d8c12a5b44633fd7d386419adfc
Status: Downloaded newer image for 376337229415.dkr.ecr.us-east-1.amazonaws.com/tweepy-stream-deploy:latest
376337229415.dkr.ecr.us-east-1.amazonaws.com/tweepy-stream-deploy:latest
```

Check pulled image shows in local docker repistory

```
$ docker images
REPOSITORY                                                          TAG       IMAGE ID       CREATED          SIZE
376337229415.dkr.ecr.us-east-1.amazonaws.com/tweepy-stream-deploy   latest    a365efc56125   36 min(t(t((((((twitter) 
```

Run docker image with entrpoint in interactive mode so can navigate and check 
folder structure

```Shell
$ docker run -it --entrypoint sh a365efc56125
```

We can see the contents of the container. We should see all the python packages 
installed and the .py scripts. 
Check the main python script with `cat` command and check it contains the latest updated code

```
sh-4.2# ls
backports			     idna-3.3.dist-info		      requests-2.27.1.dist-info
bin				     jmespath			      requests_oauthlib
boto3				     jmespath-1.0.0.dist-info	      requests_oauthlib-1.3.1.dist-info
boto3-1.21.36.dist-info		     main_twitter.py		      requirements.txt
botocore			     numpy			      s3transfer
botocore-1.24.36.dist-info	     numpy-1.22.4.dist-info	      s3transfer-0.5.2.dist-info
certifi				     numpy.libs			      secrets.py
certifi-2022.5.18.1.dist-info	     oauthlib			      six-1.16.0.dist-info
charset_normalizer		     oauthlib-3.2.0.dist-info	      six.py
charset_normalizer-2.0.12.dist-info  pandas			      tweepy
click				     pandas-1.4.1.dist-info	      tweepy-4.8.0.dist-info
click-8.0.4.dist-info		     __pycache__		      tweets_api.py
configparser-5.0.2.dist-info	     python_dateutil-2.8.2.dist-info  urllib3
configparser.py			     pytz			      urllib3-1.26.9.dist-info
dateutil			     pytz-2022.1.dist-info
idna				     requests


sh-4.2# cat main_twitter.py 
def handler(event, context):
    from tweets_api import tweepy_search_api
    from secrets import get_secrets
    import itertools
    import boto3
    import json

    code_pipeline = boto3.client("codepipeline")
    response = get_secrets(mode="aws")
    api_keys = list(itertools.islice(response.values(), 4))
    print(f"Event:{event}")
    print("Searching and delivering Tweets with Tweepy API: \n")
    # special parsing strategy for event from code pipeline as structure is nested differently
    # and of str type so need to convert to dict and parse data key
    # Executing from local_run.py or passing in event for testing lambda function
    # invocation via console - event passed to handler is already of dict type
    if isinstance(event, str):
        params = json.loads(event)["CodePipeline.job"]["data"]["actionConfiguration"][
            "configuration"
        ]["UserParameters"]
    else:
        params = event.copy()
    try:
        tweepy_search_api(params, *api_keys)
        if params["mode"] == "cloud":
            job_id = event["CodePipeline.job"]["id"]
            code_pipeline.put_job_success_result(jobId=job_id)
    except Exception as e:
        print(str(e))
        if params["mode"] == "cloud":
            job_id = event["CodePipeline.job"]["id"]
            code_pipeline.put_job_failure_result(
                jobId=job_id, failureDetails={"message": str(e), "type": "JobFailed"}
            )
        raise
```

### Setting up Deploy Stage

if Using CodeDeploy, need to do the following steps:

* Create application with Compute platform  e.g. (ECS, EC2, Lambda etc)
* Deployment-group associated with the application including the specific resources created (e.g for ECS : cluster names, 
  load balancer), service role, deployment configuration (e.g. CodeDeployDefault.OneAtATime) and traffic routing 
* Create Deployment associated with the deployment group, using the revision at the specified location e.g. S3 or by 
  using AppSpec yaml/json. A
* In Deploy Stage, using  CodeDeploy as Action Provider and the reference the application name and 
deployment group already created. 

For CloudFormation, need to do the following from console:

* select CloudFormation as Action provider in Deploy Stage in CodePipeline.
* Input Artifact would need to be the CloudFormation Template script which is output from one of the 
previous stages e.g. Source
* ActionMode will depend on whether create or update stack, delete stack or create/execute changeset.
* Template filename path with reference to the input artifact (the template filepath is generated 
automatically depending on the filename set)
* Cloud Formation RoleName
* Optional Output Artifact Name

Optionally, we can validate the cloudformation templates before deploying by using `aws cloudformation validate-template --template-url <s3_url>` 
(remote) or `aws cloudformation validate-template --template-body <file://path-to-local-file>` (local) command to check the template file 
for syntax errors. During validation, AWS CloudFormation first checks if the template is valid JSON. If it isn't, 
CloudFormation checks if the template is valid YAML. If both checks fail, CloudFormation returns a template validation 
error . Note: The `aws cloudformation validate-template` command is designed to check only the syntax of your template. It does not ensure 
that the property values that you have specified for a resource are valid for that resource. Nor does it determine 
the number of resources that will exist when the stack is created.

    
 ## References
    
* https://docs.aws.amazon.com/codebuild/latest/userguide/getting-started-create-build-project-console.html
* https://docs.aws.amazon.com/codepipeline/latest/userguide/concepts-devops-example.html
* https://docs.aws.amazon.com/codepipeline/latest/userguide/concepts.html
* https://docs.aws.amazon.com/AmazonECR/latest/userguide/docker-pull-ecr-image.html
* https://docs.aws.amazon.com/codebuild/latest/userguide/getting-started-run-build-console.html
* https://docs.aws.amazon.com/AmazonECR/latest/userguide/docker-pull-ecr-image.html
* https://docs.aws.amazon.com/AmazonECR/latest/userguide/registry_auth.html
* https://docs.aws.amazon.com/codedeploy/latest/userguide/applications-create.html
* https://docs.aws.amazon.com/codedeploy/latest/userguide/deployment-groups-create.html
* https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-validate-template.html
