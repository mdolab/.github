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

## Maintaining buildbots via ssh

For the purposes of maintaining and updating the buildbots, it is significantly to use ssh than to physically access the machines.
To do this, setup your `~/.ssh/config` file to include the following entries for buildbots 1-9:

```text
host bbot?
    User mdolab_mnt
    ControlMaster auto
    ControlPath  ~/.ssh/sockets/%r@%h-%p
    ControlPersist  600

host bbot1
    Hostname <ip_address_of_bbot1>

host bbot2
    Hostname <ip_address_of_bbot2>
.
.
.
```

You will need to use password authentication the first time you connect to each buildbot (you may need to add `PubkeyAuthentication no` under `host bbot?` to force this), then you can add your public key to the buildbots for passwordless authentication in the future by running:

```bash
ssh-copy-id -i <path_to_your_public_key> bbot<N>
```

for each buildbot.

### Ansible playbooks

This directory also contains some "Ansible playbooks" that can be run to run maintenance tasks on all the linux buildbots at once via ssh.
Once you've installed Ansible (`pip install ansible`), you can run the playbooks like so:

```bash
ansible-playbook -i inventory.ini CheckActionsService.yaml
```

Will check that the actions runner service is running on all buildbots.

```bash
ansible-playbook -i inventory.ini UpdateBBots.yml -K
```

Will update the apt packages on all buildbots and reboot them if necessary.

These commands can also be run via the bash scripts `CheckActionsService.sh` and `UpdateBBots.sh` respectively.

Note that these commands rely on you having the buildbots set up in your `~/.ssh/config` file as described above, and do not run on the mac buildbot (bbot7).
