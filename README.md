## AWS CodePipeline 

Examples of setting up CI-CD pipelines using AWS code pipeline for software delivery automation. Using CodeCommit, 
CodeBuild and CodeDeploy for versioning, building, testing and deploying applications in the cloud.

#### Setting up code commit source repo

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

Clone your repository to your local computer and start working on code. Run the following command:

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

### CodeBuild

First need to include a buildspec.yml file, which CodeBuild uses to run a build.
https://docs.aws.amazon.com/codebuild/latest/userguide/getting-started-cli-create-build-spec.html

The following documentation shows how the codebuild project can be setup
https://docs.aws.amazon.com/codebuild/latest/userguide/sample-docker.html

For Operating system, choose Ubuntu.
For Runtime, choose Standard.
For Image, choose aws/codebuild/standard:4.0.

For codebuild projects involving building docker images as in the examples in this
repo, follow the AWS doc below
https://docs.aws.amazon.com/codebuild/latest/userguide/sample-docker.html

Make sure the option, "Privileged" is ticked in build project if building docker image
Important to set the following environment variables as they are referenced to
in the buildspec.yml

* AWS_DEFAULT_REGION with a value of region-ID
* AWS_ACCOUNT_ID with a value of account-ID
* IMAGE_TAG with a value of Latest
* IMAGE_REPO_NAME with a value of Amazon-ECR-repo-name