IMAGE_REPO_NAME=${1}
AWS_ACCOUNT_ID=${3}
ROLE_NAME=${4}
CREATE_ECR_REPO=${6:-false}
AWS_DEFAULT_REGION=us-east-1
IMAGE_TAG=latest
ECR_URI=$AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/$IMAGE_REPO_NAME:$IMAGE_TAG
ROLE_ARN="arn:aws:iam::${AWS_ACCOUNT_ID}:role/${ROLE_NAME}"

echo""
echo "Docker build path set as $DOCKER_BUILD_PATH"
echo "Authenticating the Docker CLI to Amazon ECR registry"
aws ecr get-login-password --region $AWS_DEFAULT_REGION | docker login --username AWS \
      --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com


if [[ "${CREATE_ECR_REPO}" = true ]];then
  echo ""
  echo "Creating repository in Amazon ECR"
  aws ecr create-repository --repository-name $IMAGE_REPO_NAME --image-scanning-configuration scanOnPush=true \
      --image-tag-mutability MUTABLE \

fi;

if [[ $? -eq 0 ]];then
  echo ""
  echo "Building Docker image"
  docker build -t $IMAGE_REPO_NAME:$IMAGE_TAG .
fi;

if [[ $? -eq 0 ]];then
  echo ""
  echo "Tagging image to match repository name, and deploying the image to Amazon ECR using the docker push command."
  docker tag "$IMAGE_REPO_NAME":$IMAGE_TAG $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/$IMAGE_REPO_NAME:$IMAGE_TAG
  docker push $ECR_URI
fi;

