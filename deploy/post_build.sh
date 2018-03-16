#!/bin/bash

REF=`git symbolic-ref HEAD --short 2>/dev/null`
if [ "$REF" == "" ] ; then
  REF=`git branch -a --contains HEAD | sed -n 2p | awk '{ printf $1 }'`
fi

if [ "$REF" == "master" ] ; then
  echo "Running on master; build will continue."
  echo Build completed on `date`
  echo Verifying build
  docker run --entrypoint /usr/local/bin/invoke $IMAGE_REPO_NAME:$IMAGE_TAG runtests
  echo "Build verified; pushing the Docker image..."
  docker push $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/$IMAGE_REPO_NAME:$IMAGE_TAG
  echo Syncing log groups and task definitions
  python deploy/aws_setup.py
  curl -X POST --data-urlencode "payload={\"channel\": \"#labs_city_scrapers\", \"username\": \"ecs\", \"text\": \"<https://github.com/City-Bureau/documenters-aggregator/commit/$CODEBUILD_SOURCE_VERSION|Commit $CODEBUILD_SOURCE_VERSION> deployed to production. <https://console.aws.amazon.com/codebuild/home?region=us-east-1#/builds/$CODEBUILD_BUILD_ID/view/new|View build log>.\", \"icon_emoji\": \":ecs:\"}" $SLACK_WEBHOOK_URL
else
  echo "Not on the master branch; aborting."
  echo $REF
fi
