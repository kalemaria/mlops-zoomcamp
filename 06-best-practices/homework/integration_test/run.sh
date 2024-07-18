#!/usr/bin/env bash

if [[ -z "${GITHUB_ACTIONS}" ]]; then
  cd "$(dirname "$0")"
fi

if [ "${LOCAL_IMAGE_NAME}" == "" ]; then 
    LOCAL_TAG=`date +"%Y-%m-%d-%H-%M"`
    export LOCAL_IMAGE_NAME="batch-model-duration:${LOCAL_TAG}"
    echo "LOCAL_IMAGE_NAME is not set, building a new image with tag ${LOCAL_IMAGE_NAME}"
    docker build -t ${LOCAL_IMAGE_NAME} ..
else
    echo "no need to build image ${LOCAL_IMAGE_NAME}"
fi

docker-compose up -d

sleep 5

awslocal s3 mb s3://nyc-duration --endpoint-url http://localhost:4566
awslocal s3 ls --endpoint-url http://localhost:4566

export INPUT_FILE_PATTERN="s3://nyc-duration/in/{year:04d}-{month:02d}.parquet"
export OUTPUT_FILE_PATTERN="s3://nyc-duration/out/{year:04d}-{month:02d}.parquet"
export S3_ENDPOINT_URL="http://localhost:4566"

mkdir input
wget https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2023-03.parquet -P input
awslocal s3 cp input/yellow_tripdata_2023-03.parquet s3://nyc-duration/in/2023-03.parquet --endpoint-url http://localhost:4566

# run intergration test
pipenv run python integration_test.py

ERROR_CODE=$?

if [ ${ERROR_CODE} != 0 ]; then
    docker-compose logs
    docker-compose down
    exit ${ERROR_CODE}
fi

awslocal s3 ls s3://nyc-duration --recursive --endpoint-url http://localhost:4566

docker-compose down