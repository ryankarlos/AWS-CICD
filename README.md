# codepipeline
Demo of using code pipeline to build and deploy docker image for streaming tweets



```
aws lambda create-function --region sa-east-1 --function-name my-function \
    --package-type Image  \
    --code ImageUri=<ECR Image URI>   \
    --role arn:aws:iam::123456789012:role/lambda-ex 
```

```
aws lambda update-function-code --region sa-east-1 --function-name my-function \
    --image-uri <ECR Image URI>   \
```



