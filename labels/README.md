# Shared labels
This directory stores scripts and definitions of shared labels for all lab repositories, which can be applied to issues and PRs.
The script can be used to set the same labels, including description and colours, across the organization to ensure consistency.

## Using the script
First install dependencies.
- `Financial-Times/github-label-sync`, installed via `npm install github-label-sync`
- The GitHub CLI tool `gh`, which should be installed following the instructions at `cli/cli`

In order to authenticate with GitHub, two things must be done:
1. Use `gh auth` to authenticate with the CLI tool
2. Generate a PAT with write access for the organization, and save it in the environment variable `$GITHUB_TOKEN`

Now you can run `bash apply-labels.sh` which will set _all_ repos to have the same set of labels defined in `labels.yaml`.

## How does it work?
This is a 3 step process:
1. We call `gh api` using GraphQL to obtain a JSON file containing all the repos owned by the organization.
2. We call `filter-repos.py` to filter out repos which are either archived, or have the `paper` tag. This spits out a text file, with each line containing the name of the repo that meets the criteria.
3. Finally, we call `github-label-sync`, which sets the labels defined in the YAML file to all the repos in the organization. This relies on the PAT which must be defined.
