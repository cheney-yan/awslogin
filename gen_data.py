#!/usr/bin/env python
import json
import os
import configparser


def gen_config():
    config = configparser.ConfigParser()
    config.read(os.path.expanduser('~/.aws/credentials'))
    result = {}
    # only support one step of role assumption
    for section in config.sections():
        if 'aws_access_key_id' in config[section].keys():
            result[config[section].name] = {
                'aws_secret_access_key': config[section]['aws_secret_access_key']
            }
        elif 'source_profile' in config[section].keys() \
            and 'role_arn' in config[section].keys() \
                and 'aws_secret_access_key' in config[config[section]['source_profile']].keys():
            result[config[section].name] = {
                'aws_secret_access_key': config[config[section]['source_profile']]['aws_secret_access_key'],
                'assumed_role': config[section]['role_arn']
            }

    print(json.dumps(result, indent=2))

root_domain='login.python3.tech'
def gen_bookmarks():
    result=[]
    config = configparser.ConfigParser()
    config.read(os.path.expanduser('~/.aws/credentials'))
    # only support one step of role assumption
    for section in config.sections():
        if 'aws_access_key_id' in config[section].keys():
            result.append(f"https://aws.python3.tech/login?key_id={config[section]['aws_access_key_id']}&display_name={section}")
        elif 'source_profile' in config[section].keys() \
            and 'role_arn' in config[section].keys() \
                and 'aws_secret_access_key' in config[config[section]['source_profile']].keys():
            result.append(f"https://aws.python3.tech/login?key_id={config[config[section]['source_profile']]['aws_access_key_id']}&display_name={section}")


    print('\n'.join(result))


if __name__ == '__main__':
    # gen_config()
    gen_bookmarks()