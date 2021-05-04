# Azure
The MDO Lab Azure Pipelines page is found on the [Azure Website](https://dev.azure.com/mdolab/) and is split into Public and Private projects, used accordingly for public and private repositories.
The pipelines for each repository can be found by selecting its parent project and then the pipelines button.
Each pipeline is set up using the templates located in this `.github` repository so only configuration files are needed in each repository.

The templates are organized into the following files:
- `azure_build.yaml` which handles the build and test jobs for the code
- `azure_pypi.yaml` which handles the PyPI deployment if applicable
- `azure_style.yaml` which handles style checks on the code
- `azure_template.yaml` which handles the job itself, calling the necessary sub-templates.

## Template Options
| Name        | Type   | Default | Description.       |
| :---        | :---- | :----  |               :--- |
| `REPO_NAME`   | string |         | Name of repository |
| `IGNORE_STYLE`| boolean | `false`| Allow black and flake8 jobs to fail without failing the pipeline |
| `ISORT`| boolean | `false`| Runs the `isort` jobs if `true` |
| `COMPLEX` | boolean | `false` | Flag for triggering complex build and tests |
| `GCC_CONFIG` | string | `None` | Path to gcc configuration file (from repository root) |
| `INTEL_CONFIG` | string | `None` | Path to intel configuration file (from repository root) |
| `BUILD_REAL` | string | `.github/build_real.sh` | Path to bash script with commands to build real code. Using `None` will skip this step. |
| `TEST_REAL` | string | `.github/text_real.sh` | Path to bash script to run real tests. Using `None` will skip this step. |
| `BUILD_COMPLEX` | string | `.github/build_complex.sh` | Path to bash script with commands to build complex code. Using `None` will skip this step. |
| `TEST_COMPLEX` | string | `.github/text_complex.sh` | Path to bash script with commands to run complex tests. Using `None` will skip this step. |
| `IMAGE` | string | `public` | Select docker image. Can be `public`, `private`, or `auto`. `auto` uses the private image on trusted builds and the public image otherwise. |
| `SKIP_TESTS` | boolean | `false` | Skip all builds and tests |
| `TIMEOUT` | number | `0` (this will use the full 360 minutes) | Runtime allowed for a job, in minutes |
| `COVERAGE` | boolean | `false` | Flag to report test coverage to `codecov` |


## Setting up a pipeline
### Step 1: Setup Azure Pipelines YAML File:

1. Create `azure_template.yaml` in the `.github/` directory of your repository
2. Add triggers (see example below)
 	- Only set triggers for the `master` branch and pull requests to `master`
3. Add resources (see example below)
	- This resource pulls the `azure_template` from the `mdolab/.github` repository
4. Add parameters (see example below and the options table above)

```
trigger:
- master

pr:
- master

resources:
  repositories:
  - repository: azure_template
    type: github
    name: mdolab/.github
    endpoint: mdolab

extends:
  template: azure/azure_template.yaml@azure_template
  parameters:
    REPO_NAME: adflow
    IGNORE_STYLE: true
    COMPLEX: true
    GCC_CONFIG: config/defaults/config.LINUX_GFORTRAN.mk
    INTEL_CONFIG: config/defaults/config.LINUX_INTEL.mk
```

### Step 2: Write Build Bash Script:

1. Create `build_real.sh` in the `.github/` directory of your repository
2. Add `#!/bin/bash` followed by `set -e` as the first two lines
3. Add configuration file copy if needed (see example below). Note that the environment variable `$CONFIG_FILE` is provided by the Azure template and is automatically set depending on the compiler used for each build.
4. Add make command if needed (see example below)
5. Add python install command (see example below)
6. Repeat with `build_complex.sh` if needed

```
#!/bin/bash
set -e
cp $CONFIG_FILE config/config.mk
make
pip install .
```

### Step 3: Write Test Bash Script:

1. Create `test_real.sh` in `.github/` directory of your repository
2. Add `#!/bin/bash` followed by `set -e` as the first two lines
3. Add input file download if needed (see example below)
4. Add `testflo` command
5. Repeat with `test_complex.sh` if needed

```
#!/bin/bash
set -e
./input_files/get-input-files.sh
testflo -v . -n 1
```

### Step 4: Push branch to `mdolab/` repository and create pull request

1. Push branch directly to `mdolab` repository, not your personal fork

### Step 5: Create new Pipeline on Microsoft Azure

1. Go to [Azure Pipelines](https://dev.azure.com/mdolab/) and select public / private as needed by current repository
2. Select "Pipelines" and "New pipeline"
3. Select "Github" and authorize the Azure Pipeline app if you have not already
4. Select correct mdolab repository (again, not personal fork)
5. Select "Existing Azure Pipelines YAML file"
6. In pop-up menu, set "Branch" to your new Azure-transition branch and "Path" to `.github/azure-pipelines.yaml`
7. Click "continue"

### Step 6: Add Badge to README

1. Go to the pipeline on Azure
2. Click on the three dots next to "Run pipeline"
3. Click on "status badge"
4. Set "Branch" to "master"
5. Copy the text for "Sample markdown" and paste it into README

### Step 7: Create PR

1. Create pull request to `master`
2. Ensure the Azure jobs start and appear in the pull request

## PyPI with Azure
If using PyPI for a repository, the yaml file does not follow this same structure, but imports components as stages instead of as an extend.
An example yaml file using PyPI is:

```
trigger:
  branches:
    include:
    - master
  tags:
    include:
    - v*.*.*

pr:
- master

resources:
  repositories:
  - repository: azure_template
    type: github
    name: mdolab/.github
    endpoint: mdolab

stages:
- template: azure/azure_template.yaml@azure_template
  parameters:
    REPO_NAME: REPOSITORY NAME

- stage:
  dependsOn:
  - Test_Real
  - Style
  displayName: PyPI
  condition: and(succeeded(), contains(variables['build.sourceBranch'], 'tags'))
  jobs:
  - template: azure/azure_pypi.yaml@azure_template
```
