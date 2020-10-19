#!/bin/bash
set -ev

# We throw away the existing repo in Docker, and copy the new one in-place
docker exec -it app /bin/bash -c "rm -rf $DOCKER_WORKING_DIR && cp -r $DOCKER_MOUNT_DIR $DOCKER_WORKING_DIR"

# Copy over the correct config file and modify as needed
docker exec -it app /bin/bash -c ". $BASHRC && cd $DOCKER_WORKING_DIR && cp $CONFIG_MK config/config.mk";

# compile real build
if [[ "$DOCKER_TEST_TYPE" == "real" ]]; then
    docker exec -it app /bin/bash -c ". $BASHRC && cd $DOCKER_WORKING_DIR && make"
fi

# compile complex build iff complex makefile exists, and either TEST_TYPE=complex OR not separate build
# we only check the makefile in the Travis VM, no need to check in Docker
if [[ "$SEPARATE_COMPLEX_BUILD" != true || "$DOCKER_TEST_TYPE" == "complex" ]] && [ -f "Makefile_CS" ]; then
    docker exec -it app /bin/bash -c ". $BASHRC && cd $DOCKER_WORKING_DIR && make -f Makefile_CS PETSC_ARCH=complex-opt-\$COMPILERS-\$PETSCVERSION";
fi

# Install Python interface
docker exec -it app /bin/bash -c ". $BASHRC && cd $DOCKER_WORKING_DIR && pip install ."
