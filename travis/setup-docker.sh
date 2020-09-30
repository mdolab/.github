#!/bin/bash
set -ev

# login to Docker using Travis encrypted credentials
if [[ "$DOCKER_REPO" == "private" ]]; then
    echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin;
fi

docker pull mdolab/$DOCKER_REPO:$DOCKER_TAG
# run Docker, key is we mount the current Travis directory into Docker to access content of repo
docker run -t -d \
    --name app \
    --mount "type=bind,src=$(pwd),target=$DOCKER_MOUNT_DIR" \
    mdolab/$DOCKER_REPO:$DOCKER_TAG \
    /bin/bash

# set compiler based on docker tag
if [[ "$DOCKER_TAG" == *"intel"* ]]; then
    export COMPILER=intel;
    export CONFIG_MK=$INTEL_CONFIG;
else
    export COMPILER=gcc;
    export CONFIG_MK=$GCC_CONFIG;
fi

# We throw away the existing repo in Docker, and copy the new one in-place
docker exec -it app /bin/bash -c "rm -rf $DOCKER_WORKING_DIR && cp -r $DOCKER_MOUNT_DIR $DOCKER_WORKING_DIR"
