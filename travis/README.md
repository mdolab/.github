# Travis configurations
This subdirectory contains default Travis configurations which are shared across the MDO Lab organization.
These can then be imported by the `.travis.yml` file in each repo to ensure consistency.

## Jobs
The jobs are defined in the `jobs-env.yml` file.
By default the following jobs are queued:
- `flake8` tests with `TEST_TYPE=flake8`, one per Python version
- `black` tests with `TEST_TYPE=black`, one per Python version
- Docker tests with `TEST_TYPE=docker` and `DOCKER_TEST_TYPE=real`, one per `DOCKER_TAG`

In addition, if the variable `SEPARATE_COMPLEX_BUILD` is set to `true`, then another set of Docker tests are triggered, with `DOCKER_TEST_TYPE=complex`.
This is meant to facilitate repos that would benefit from separate real and complex tests, and to take advantage of the job concurrency available on Travis (currently 8 for public and 2 for private repos).
However, even for repos with both real and complex tests, it's not necessary to use this feature, since it is not activated by default and you can simply run both real and complex tests in the same job.
In this case, you would ignore the `DOCKER_TEST_TYPE` variable and lump both tests together.

## How do I use this?
These scripts are designed to be somewhat flexible in nature, configurable by selectively importing files and setting various environment variables.
The most common use case is to have Travis trigger `black`, `flake8`, and a set of Docker builds.
For the Docker builds, follow the "standard" MDO Lab build process, and if successful run the testing script.
To do this, create a `.travis.yml` file in the root of your repository that you want to test with Travis, import all three `.yml` files, and setting the following variables:
- `DOCKER_REPO` (by default this is set to `public` so only modify this if you need the `private` images)
- `GCC_CONFIG` and `INTEL_CONFIG` should point to the `gcc` and `intel` config files
- Optionally, set `SEPARATE_COMPLEX_BUILD=true` to have another set of complex builds triggered

The `DOCKER_REPO` variable controls whether the Docker image is `public` or `private`.
It's also possible to have Travis automatically determine the `DOCKER_REPO` value by setting `AUTO_DOCKER_REPO=true`.
This will set `DOCKER_REPO` to `public` if it is a PR build from another user, and `private` if it's a PR build from `mdolab` or a branch build.
This is used by pyOptSparse which performs tests using either image depending on whether the Docker Hub credentials are available.

Then, the only stage you need to define is the `script` portion, which should contain simple bash commands for running the tests.
Note that this must be wrapped with `if [ $TEST_TYPE == "docker" ]; then` since we only want this run on the Docker tests.
If you triggered separate real/complex builds, you should also wrap the real and complex testing steps with these bash conditionals.
See ADflow or IDwarp for examples.

## Overriding the install step
For some repos, the default install step may not work.
This could be due to having just a single `config.mk` file, or requiring a totally different process to build the code.
In such cases, do not import the `install.yml` file, and manually define everything in the `.travis.yml` file in the specific repo.
See cgnsUtilities and pygeo for examples.

In some cases, you may also want Travis to NOT replace the existing package directory in Docker. This is the case for pyOptSparse, where the proprietary codes contained in the Docker image must be backed up prior to overwriting with the content of the build. To do this, set `SKIP_COPY_DIR=true`.

## Additional environment variables
Several other environment variables are available for use:
- `REPO_NAME` points to the name of the repository that triggered the build
- `PR_FROM` points to the origin of the PR. If the PR is triggered from `mdolab` then it will be set to `mdolab`, and for branch builds it will be empty.
This can be used to select the Docker repo, pulling from `public` on a PR build, but `private` for a trusted PR build or a branch build.

There are also some variables defined for internal use:
- convenience variables used by some of the other imported scripts such as `DOCKER_WORKING_DIR`, `DOCKER_MOUNT_DIR`, and `BASHRC`
- secure Docker Hub credentials for accessing private Docker images. These are only available on "trusted" builds, i.e. those triggered by the `mdolab` organization
