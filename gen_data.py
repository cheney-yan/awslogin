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
            result.append(f"<DT><A HREF=\"https://aws.python3.tech/login?key_id={config[section]['aws_access_key_id']}&display_name={section}\">{section}</A>")
        elif 'source_profile' in config[section].keys() \
            and 'role_arn' in config[section].keys() \
                and 'aws_secret_access_key' in config[config[section]['source_profile']].keys():
            result.append(f"<DT><A HREF=\"https://aws.python3.tech/login?key_id={config[config[section]['source_profile']]['aws_access_key_id']}&display_name={section}\">{section}</A>")

    print ("""<!DOCTYPE NETSCAPE-Bookmark-file-1>
<!-- This is an automatically generated file.
     It will be read and overwritten.
     DO NOT EDIT! -->
<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">
<TITLE>Bookmarks</TITLE>
<H1>Bookmarks</H1>
<DL><p>
    <DT><H3 ADD_DATE="1599984168" LAST_MODIFIED="1605593638" PERSONAL_TOOLBAR_FOLDER="true">Bookmarks Bar</H3>
    <DL><p>
        <DT><H3 ADD_DATE="1605063829" LAST_MODIFIED="0">AWS ACC</H3>
        <DL><p>
        """)
    print('\n'.join(result))

    print("""
            </DL><p>
        </DL><p>
</DL><p>
    
""")
if __name__ == '__main__':
    # gen_config()
    gen_bookmarks()