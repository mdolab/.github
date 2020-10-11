#!/bin/bash
set -ev

# Copy over the correct config file and modify as needed
docker exec -it app /bin/bash -c ". $BASHRC && cd $DOCKER_WORKING_DIR && cp $CONFIG_MK config/config.mk";
if [[ "$TEST_COMPLEX" != "true" ]]; then # compile real build
    docker exec -it app /bin/bash -c ". $BASHRC && cd $DOCKER_WORKING_DIR && make"
elif [[ "$TEST_COMPLEX" == "true" ]] && [ -f "Makefile_CS" ]; then # compile complex build iff complex makefile exists
    # we only check the makefile in the Travis VM, no need to check in Docker
    docker exec -it app /bin/bash -c ". $BASHRC && cd $DOCKER_WORKING_DIR && make -f Makefile_CS PETSC_ARCH=complex-opt-\$COMPILERS-\$PETSCVERSION";
fi
# Install Python interface
docker exec -it app /bin/bash -c ". $BASHRC && cd $DOCKER_WORKING_DIR && pip install ."
