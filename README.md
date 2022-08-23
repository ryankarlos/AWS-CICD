## AWS CodePipeline 


In this example, we will  configure AWS CodePipeline to build an ECR image and deploy the latest version 
to lambda container. The application code will stream tweets using python tweepy library. First we need to setup code pipeline and the various stages to deploy application code to lambda image 
which will stream tweets when invoked.
Please refer to [readme](projects/deploy-lambda-image/README.md) for instructions on how to run the demo.