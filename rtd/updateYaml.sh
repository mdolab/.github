#!/bin/bash

USAGE="
usage: -l LAYER -t DOCKER_TAG_NAME

Description:
This script generates a .readthedocs.yaml file for a given repository and
copies it to the proper location within the repository.

Argument description:
    -a|--commit            Commit yaml file changes to a new branch
    -p|--push-branch       Push the branch to GH
    -c|--create-gh-prs     Create GH PRs
"

die () {
    echo "Something went wrong. See logs for details... EXITING"
    exit 9
}

# Parse input
COMMIT=0
PUSH_BRANCH=0
CREATE_GH_PRS=0
while [[ "$#" -gt 0 ]]; do
    case $1 in
        -a|--commit) COMMIT=1 ;;
        -p|--push-branch ) PUSH_BRANCH=1 ;;
        -c|--create-gh-prs ) CREATE_GH_PRS=1 ;;
        -h|--help) echo "$USAGE";  exit 1 ;;
        *) echo "Unknown parameter passed: $1"; echo "$USAGE"; exit 1 ;;
    esac
    shift
done

ROOTDIR=$(pwd)

REPOS=(
#"adflow"
#"baseclasses"
#"cgnsutilities"
# "CMPLXFOIL"
# "complexify"
# "dev-tutorials"
# "idwarp"
# "MACH-Aero"
# "privat"
# "multipoint"
# "niceplots"
# "OpenAeroStruct"
# "openconcept"
# "performancecalcs"
# "prefoil"
# "private-docs"
# "pyaerostructure"
# "pyfriction"
# "pygeo"
# "pyhyp"
# "pylayout"
# "pyoptsparse"
# "pyspline"
# "pysurf"
# "pytacs"
# "pyXDSM"
# "tacs_orig"
# "VACC"
"weightandbalance"
#"wimpresscalc"
)

BRANCH_NAME="updateRtdYaml"

## First create a tmp directory in the current directory
WORKDIR="$ROOTDIR/tmp"
rm -rf $WORKDIR && mkdir -p $WORKDIR
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

    if [[ $COMMIT -eq 1 ]]; then
        git add .readthedocs.yaml
        git commit -m "update .readthedocs.yaml"

        # Push branch
        if [[ $PUSH_BRANCH -eq 1 ]]; then
            git push --set-upstream origin $BRANCH_NAME

            # Create the PR on GH
            if [[ $CREATE_GH_PRS -eq 1 ]]; then
                gh pr create --fill
            fi
        fi
    fi
done