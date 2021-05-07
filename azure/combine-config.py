"""
This script will read in two files via command line arguments
It will then merge them, and write it out to the appropriate output file name
"""
import argparse
import configparser

parser = argparse.ArgumentParser()
parser.add_argument("default", type=str, help="file name for the default config file")
parser.add_argument("repo", type=str, help="file name for the repo-specific config file")
parser.add_argument("output", type=str, help="output file name")
args = parser.parse_args()

# default config
config_def = configparser.ConfigParser()
config_def.read(args.default)
# project config
config_repo = configparser.ConfigParser()
config_repo.read(args.repo)

# merge them together, with existing keys overwritten by project config
for config in config_def.keys():
    for key in config_repo[config].keys():
        config_def[config][key] = config_repo[config][key]

# write out the file
with open(args.output, "w") as configfile:
    config_def.write(configfile)
