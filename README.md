# .github
This repo stores the following shared repository settings/configurations/templates:
- Issue and pull request templates on GitHub
- Shared configurations for Azure Pipelines

Azure
=====
The MDO Lab Azure Pipelines page is found on the [Azure Website](https://dev.azure.com/mdolab/) and is split into Public and Private projects, used accordingly for public and private repositories.
The pipelines for each repository can be found by selecting is parent project and then the pipelines button.
Each pipline is set up using the templates located in this `.github` repository so only configuration files are needed in each repository.

The templates are organized into `azure_build.yaml` which handles the build and test jobs for the code, `azure_pypi.yaml` which handles the PyPI deployment if applicable, `azure_style.yaml` which handles style checks on the code, and `azure_template.yaml` which handles the job iteself, calling the necessary subtemplates.

Template Options
----------------
| Name        | Type   | Default | Description.       |
| :---        | :---- | :----  |               :--- |
| REPO_NAME   | string |         | Name of repository |
| IGNORE_STYLE| boolean | false| Allow black and flake8 jobs to fail without failing the pipeline |
| COMPLEX | boolean | false | Flag for triggering complex build and tests |
| GCC_CONFIG | string | None | Path to gcc configuration file (from repository root) |
| INTEL_CONFIG | string | None | Path to intel configuration file (from repository root) |
| BUILD_REAL | string | .github/build_real.sh | Path to bash script with commands to build real code. Using "None" will skip this step. |
| TEST_REAL | string | .github/text_real.sh | Path to bash script to run real tests. Using "None" will skip this step. |
| BUILD_COMPLEX | string | .github/build_complex.sh | Path to bash script with commands to build complex code. Using "None" will skip this step. |
| TEST_COMPLEX | string | .github/text_complex.sh | Path to bash script with commands to run complex tests. Using "None" will skip this step. |
| IMAGE | string | public | Select docker image. Can be "public", "private", or "auto". "auto" uses the private image on trusted builds and the public image otherwise. |
| SKIP_TESTS | boolean | false | Skip all builds and tests |
| TIMEOUT | number | 0 (360 minutes) | Runtime allowed for a job, in minutes |


Setting up a pipeline
---------------------
**Step 1: Setup Azure Pipelines YAML File:**

- Create `azure_template.yaml` in the `.github/` directory of your repository
- Add triggers (see example below)
 	- Only set triggers for the `master` branch and pull requests to `master`
- Add resources (see example below)
	- This resource pulls the `azure_template` from the `mdolab/.github` repository
- Add parameters (see example below and the options table above)

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

**Step 2: Write Build Bash Script:**

- Create `build_real.sh` in the `.github/` directory of your repository
- Add `#!/bin/bash` followed by `set -e` as the first two lines
- Add configuration file copy (if needed) (see example below)
- Add make command (if needed) (see example below)
- Add python install command (see example below)
- Repeat with `build_complex.sh` if needed

```
#!/bin/bash
set -e
cp $CONFIG config/config.mk
make
pip install .
```

**Step 3: Write Test Bash Script:**

- Create `test_real.sh` in `.github/` directory of your repository
- Add `#!/bin/bash` followed by `set -e` as the first two lines
- Add input file download (if needed) (see example below)
- Add testflo command
- Repeat with `test_complex.sh` if needed

```
#!/bin/bash
set -e
./input_files/get-input-files.sh
testflo -v . -n 1
```

**Step 4: Push branch to `mdolab/` repository and create pull request**

- Push branch directly to `mdolab` repository, not your personal fork

**Step 5: Create new Pipeline on Microsoft Azure**

- Go to [Azure Pipelines](https://dev.azure.com/mdolab/) and select public / private as needed by current repository
- Select "Pipelines" and "New pipeline"
- Select "Github" and authorize the Azure Pipeline app if you have not already
- Select correct mdolab repository (again, not personal fork)
- Select "Existing Azure Pipelines YAML file"
- In pop-up menu, set "Branch" to your new Azure-transition branch and "Path" to `.github/azure-pipelines.yaml`
- Click "continue"

**Step 6: Add Badge to README**

- Go to the pipeline on Azure
- Click on the three dots next to "Run pipeline"
- Click on "status badge"
- Set "Branch" to "master"
- Copy the text for "Sample markdown" and paste it into README

**Step 7: Create PR**

- Create pull request to `master`
- Ensure the Azure jobs start and appear in the pull request

PyPI with Azure
---------------
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
