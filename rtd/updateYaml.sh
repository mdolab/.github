#!/bin/bash

USAGE="
usage: -l LAYER -t DOCKER_TAG_NAME

Description:
This script generates a .readthedocs.yaml file for a given repository and
copies it to the proper location within the repository.

Argument description:
    -w|--work-level     0: Clone and copy yaml file to repository (default)
                        1: Commit yaml file changes to a new branch
                        2: Push the branch to GH
                        3: Create GH PRs
    -r|--repo           Repository that should be updated. If not specified
                        an internal list of repositories will used.
    -h|--help           Print this help
"

die () {
    echo "Something went wrong. See logs for details... EXITING"
    exit 9
}

# Parse input
WORK_LEVEL=0
MANUAL_REPO=""
while [[ "$#" -gt 0 ]]; do
    case $1 in
        -w|--work-level) WORK_LEVEL="$2"; shift ;;
        -r|--repo ) MANUAL_REPO="$2"; shift ;;
        -h|--help) echo "$USAGE";  exit 1 ;;
        *) echo "Unknown parameter passed: $1"; echo "$USAGE"; exit 1 ;;
    esac
    shift
done

ROOTDIR=$(pwd)

# If input is specified then we only use that
if [[ ! -z $MANUAL_REPO ]]; then
    REPOS=("$MANUAL_REPO")
else
    # otherwise set use a default list
    REPOS=(
        "adflow"
        "baseclasses"
        "cgnsutilities"
        "CMPLXFOIL"
        "complexify"
        "dev-tutorials"
        "idwarp"
        "MACH-Aero"
        "private-mach-aero"
        "multipoint"
        "performancecalcs"
        "prefoil"
        "private-docs"
        "pyaerostructure"
        "pyfriction"
        "pygeo"
        "pyhyp"
        "pylayout"
        "pyoptsparse"
        "pyspline"
        "pysurf"
        "pytacs"
        "pyXDSM"
        "tacs_orig"
        "weightandbalance"
        "wimpresscalc"
    )
fi

# Create a working tmp directory to hold the working
WORKDIR="$ROOTDIR/tmp"
rm -rf $WORKDIR && mkdir -p $WORKDIR

BRANCH_NAME="updateRtdYaml"
RTD_PR_TEMPATE_FILE=$WORKDIR/RTD_PR_TEMPATE.md
cat > $RTD_PR_TEMPATE_FILE << EOF
## Purpose
Update \`.readthedocs.yaml\` file

## Expected time until merged
Few days

## Type of change
- [ ] Bugfix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (non-backwards-compatible fix or feature)
- [ ] Code style update (formatting, renaming)
- [ ] Refactoring (no functional changes, no API changes)
- [x] Documentation update
- [x] Maintenance update
- [ ] Other (please describe)

EOF

for i in ${!REPOS[@]}; do
    # Reset to
    cd $WORKDIR
    repo=${REPOS[$i]}
    REPODIR="$WORKDIR/$repo"
    echo "Updating $repo"
    git clone git@github.com:mdolab/"$repo".git
    cd $REPODIR
    git checkout -b $BRANCH_NAME

    # Generate the yaml file (just copy for now)
    # python genYaml.py
    cp $ROOTDIR/.rtd.yaml $REPODIR/.readthedocs.yaml

    # Commit the changes
    if [[ $WORK_LEVEL -ge 1 ]]; then
        git add .readthedocs.yaml
        git commit -m "update .readthedocs.yaml"

        # Push branch
        if [[ $WORK_LEVEL -ge 2 ]]; then
            git push --set-upstream origin $BRANCH_NAME

            # Create the PR on GH
            if [[ $WORK_LEVEL -ge 3 ]]; then
                gh pr create --title "Update .readthedocs.yaml" --body-file "$RTD_PR_TEMPATE_FILE"
            fi
        fi
    fi
done