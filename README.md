## AWS CodePipeline 

Here we will demonstate an examples of setting up CI-CD pipelines using AWS code pipeline for software delivery automation. Using CodeCommit, 
CodeBuild and CodeDeploy for versioning, building, testing and deploying applications in the cloud.
We will configure AWS CodePipeline to build an ECR image and deploy the latest version to lambda container.
The application code will stream tweets using tweepy library to kinesis stream.
First we need to setup codepipeline and he various stages before invoking our lambda to stream tweets. Once this is complete, 
navigate to this [page](projects/deploy-lambda-image) to setup kinesis stream resource and stream tweets to it.

### Setting up Code Pipeline 

Typically a codepipeline job contains the following stages but could be fewer or more depending on the application for e.g. could have more envs for testing before deplopyoing to 
prod.  [1][2].


* **Source**
In this step the latest version of our source code will be fetched from our repository and uploaded to an S3 bucket.
The application source code is maintained in a repository configured as a GitHub source action in the pipeline. 
When developers push commits to the repository, CodePipeline detects the pushed change, and a pipeline execution 
starts from the Source Stage. The GitHub source action completes successfully (that is, the latest changes 
have been downloaded and stored to the artifact bucket unique to that execution). The output artifacts 
produced by the GitHub source action, which are the application files from the repository, are then used as 
the input artifacts to be worked on by the actions in the next stage.  [1][2].
  
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
requires manual approval to execute [3]


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

Create a new code commit repository using the command below in cli [10]

```shell
aws codecommit create-repository --repository-name MyDemoRepo --repository-description "My demonstration repository" 
```

Clone your repository to your local computer and start working on code. Run the following 
[command](https://docs.aws.amazon.com/codecommit/latest/userguide/how-to-connect.html) 
You can get the ssh uri from the console under Clone URL for the code commit repo

```shell
$ git clone ssh://git-codecommit.us-east-1.amazonaws.com/v1/repos/MyDemoRepo 
```
You can get the ssh uri from the console under Clone URL for the code commit repo

#### Optional: Configuring pushing to both CodeCommit and Github

Since code in codecommit and github cannot be automatically synced, you can configure git to push 
to both code commit and github repos when running `git push origin master`

When ssh codecommit repo to local, remote url is set automatically for 
fetch and push.

```shell
$ git remote -v
origin	ssh://git-codecommit.us-east-1.amazonaws.com/v1/repos/deploy-lambda-image (fetch)
origin	ssh://git-codecommit.us-east-1.amazonaws.com/v1/repos/deploy-lambda-image (push)
`

we will have to manually add an extra push-url for github repo 

```shell
$ git remote set-url --add --push git://another/repo.git
```

origin maps to both github and aws code commit repo urls for git push actions

```shell
$ git remote -v
origin	ssh://git-codecommit.us-east-1.amazonaws.com/v1/repos/codecommit_dockerbuild (fetch)
origin	git@github.com:ryankarlos/codepipeline.git (push)
origin	ssh://git-codecommit.us-east-1.amazonaws.com/v1/repos/codecommit_dockerbuild (push)
```

Note: May need to run the following to add ssh key if get `Permission denied (publickey)` error when
trying to push to remote

```shell
$ ssh-add --apple-use-keychain ~/.ssh/codecommit_rsa
```

#### Other Actions in Source Stage

We could also use the source stage to read in other files and output them as artifacts to be
used in downstream stages in pipeline. E.g. reading template configs zipped folder from S3 and using that as
input artifact to CloudFormation stack.


### Setting up Build Stage

First need to include a buildspec.yml file, which CodeBuild uses to run a build. [4][9]

Then you create a build project that AWS CodeBuild uses to run the build. A build project 
includes information about how to run a build, including where to get the source code, which 
build environment to use, which build commands to run, and where to store the build output [6][7].


For Operating system, choose Ubuntu.
For Runtime, choose Standard.
For Image, choose aws/codebuild/standard:4.0.


For codebuild projects involving building docker image to push to ECR, follow the AWS doc below [8]
Make sure the option, "Privileged" is ticked in build project if building docker image
Also, Important to set the following environment variables as they are referenced to
in the buildspec.yml

* AWS_DEFAULT_REGION with a value of region-ID
* AWS_ACCOUNT_ID with a value of account-ID
* IMAGE_TAG with a value of Latest
* IMAGE_REPO_NAME with a value of Amazon-ECR-repo-name


#### Optional: Checking docker image contents from ECR

For images built from CodeBuild and pushed to ECR, if you want to check contents or run docker image locally from 

Amazon ECR, you can pull it to your local environment with the docker pull command. [4]

First you would need to authenticate your Docker client to the Amazon ECR registry that you intend to pull your image from. 
Authentication tokens must be obtained for each registry used, and the tokens are valid for 12 hours [5].

The following command can be run, replacing <AWS-ACCOUNT-ID> with AWS account id.

```shell
$ aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <AWS-ACCOUNT-ID>.dkr.ecr.us-east-1.amazonaws.com
Login Succeeded
```

Pull the image using the docker pull command below. Add the latest tag to pull the  latest image update. [3]

```shell
$ docker pull 376337229415.dkr.ecr.us-east-1.amazonaws.com/tweepy-stream-deploy:latest
```

Check pulled image shows in local docker repistory

```shell
$ docker images

REPOSITORY                                                          TAG       IMAGE ID       CREATED          SIZE
376337229415.dkr.ecr.us-east-1.amazonaws.com/tweepy-stream-deploy   latest    a365efc56125   36 min(t(t((((((twitter) 
```

Run docker image with entrpoint in interactive mode so can navigate and check 
folder structure

```shell
$ docker run -it --entrypoint sh a365efc56125
```

We can see the contents of the container. We should see all the python packages 
installed and the .py scripts. 
Check the main python script with `cat` command and check it contains the latest updated code

```shell
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

* Create application with Compute platform  e.g. (ECS, EC2, Lambda etc) [11].
* Deployment-group associated with the application including the specific resources created (e.g for ECS : cluster names, 
  load balancer), service role, deployment configuration (e.g. CodeDeployDefault.OneAtATime) and traffic routing [12].
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
error [13]. **Note**: The `aws cloudformation validate-template` command is designed to check only the syntax of your template. It does not ensure 
that the property values that you have specified for a resource are valid for that resource. Nor does it determine 
the number of resources that will exist when the stack is created.

## References

* 1.  https://docs.aws.amazon.com/codepipeline/latest/userguide/concepts-devops-example.html
* 2. https://docs.aws.amazon.com/codepipeline/latest/userguide/concepts.html
* 3. https://docs.aws.amazon.com/codepipeline/latest/userguide/approvals-action-add.html.
* 4.  https://docs.aws.amazon.com/AmazonECR/latest/userguide/docker-pull-ecr-image.html
* 5.  https://docs.aws.amazon.com/AmazonECR/latest/userguide/registry_auth.html
* 6.  https://docs.aws.amazon.com/codebuild/latest/userguide/getting-started-create-build-project-console.html
* 7.  https://docs.aws.amazon.com/codebuild/latest/userguide/getting-started-run-build-console.html
* 8.  https://docs.aws.amazon.com/codebuild/latest/userguide/sample-docker.html
* 9. https://docs.aws.amazon.com/codebuild/latest/userguide/getting-started-cli-create-build-spec.html
* 10. https://docs.aws.amazon.com/codecommit/latest/userguide/how-to-create-repository.html
* 11. https://docs.aws.amazon.com/codedeploy/latest/userguide/applications-create.html
* 12. https://docs.aws.amazon.com/codedeploy/latest/userguide/deployment-groups-create.html
* 13. https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-validate-template.html
