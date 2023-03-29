# MDOLab BuildBot Setup

This directory contains the script that should almost entirely automate the setup of a BuildBot for running Github actions for MDOLab repos.

## Installation steps

1. Install a minimal version of the latest Ubuntu LTS version on the machine, use the following when setting up the user account:
   1. **Your name:** `mdolabbuildbot-N` (replace "N" is the next available buildbot number)
   2. **Your computer's name:** `mdolabbuildbot-N`
   3. **Pick a username:** `mdolab_mnt`
   4. **Choose a password:** ask one of our GitHub organization admins for this
2. Download this directory to somewhere like `~/buildbot`
3. Get one of our GitHub organization admins to generate a new token for you
4. Run `bash buildbot_setup.sh` and follow the prompts
5. If the process finished successfully, check that the actions runner is running using `systemctl list-units --type=service --state=running`, you should see a line that looks like `actions.runner.mdolab.mdolabbuildbot-N.service loaded active running GitHub Actions Runner (mdolab.mdolabbuildbot-N)`
6. Just to be sure everything is working, reboot the machine and repeat the check above
