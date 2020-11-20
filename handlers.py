#!/usr/bin/env python
# -*- coding: utf-8 -*-
import botocore
import logging
import urllib
import os
import json
import boto3
import configparser

import requests
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
allow_all_policy = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Action": "*",
            "Effect": "Allow",
            "Resource": "*"
        }
    ]
}


def get_profile_config():
    bucket = os.environ['credential_bucket']
    key = os.environ['credential_key']
    logger.info("Retrieving credentials from s3://%s/%s",
                bucket, key)
    local_file_path = '/tmp/profiles.json'
    s3 = boto3.resource('s3')
    s3.Bucket(bucket).download_file(key, local_file_path)

    with open(local_file_path) as f:
        return json.load(f)


def aws_signin_url(key_id, display_name, time_to_live=None):
    credentials_config = get_profile_config()
    logger.info("Retrieving from key id: %s, profile name: %s",
                key_id, display_name)
    access_key = credentials_config[display_name]['aws_secret_access_key']
    session = boto3.Session(aws_access_key_id=key_id,
                            aws_secret_access_key=access_key)
    assumed_role = credentials_config[display_name].get('assumed_role')
    sts_client = session.client('sts')
    if not assumed_role:  # using the profile directly
        if not time_to_live:
            time_to_live = 129600
        else:
            time_to_live = int(time_to_live)
        logger.debug("Retriving using key_id %s, key ***%s", key_id, access_key[-3:-1])
        credentials = sts_client.get_federation_token(
            Name=display_name,
            DurationSeconds=time_to_live,
            Policy=json.dumps(allow_all_policy)
        ).get('Credentials')
    else:
        if not time_to_live:
            time_to_live = 43200
        else:
            time_to_live = int(time_to_live)
        credentials = sts_client.assume_role(
            RoleArn=assumed_role,
            RoleSessionName=display_name
        ).get('Credentials')
    # Format credentials into JSON
    json_string_with_temp_credentials = '{'
    json_string_with_temp_credentials += '"sessionId":"' + \
        credentials.get('AccessKeyId') + '",'
    json_string_with_temp_credentials += '"sessionKey":"' + \
        credentials.get('SecretAccessKey') + '",'
    json_string_with_temp_credentials += '"sessionToken":"' + \
        credentials.get('SessionToken') + '"'
    json_string_with_temp_credentials += '}'

    # Make request to AWS federation endpoint to get sign-in token. Construct the parameter string with
    # the sign-in action request, a 12-hour session duration, and the JSON document with temporary credentials
    # as parameters.
    if not assumed_role:
        request_parameters = '?Action=getSigninToken&Session={cred_json}'.format(
            cred_json=urllib.parse.quote(json_string_with_temp_credentials),
        )
    else:
        request_parameters = '?Action=getSigninToken&SessionDuration={duration_sec}&Session={cred_json}'.format(
            duration_sec=time_to_live,
            cred_json=urllib.parse.quote(json_string_with_temp_credentials),
        )
    request_url = "https://signin.aws.amazon.com/federation" + request_parameters
    r = requests.get(request_url)
    # Returns a JSON document with a single element named SigninToken.
    signin_token = r.json()

    # Create URL where users can use the sign-in token to sign in to
    # the console. This URL must be used within 15 minutes after the
    # sign-in token was issued.
    request_parameters = '?Action=login&Issuer={issuer}&Destination={destination}&SigninToken={signin_token}'.format(
        issuer=display_name,
        destination=urllib.parse.quote("https://console.aws.amazon.com/"),
        signin_token=signin_token["SigninToken"]
    )
    request_url = "https://signin.aws.amazon.com/federation" + request_parameters
    return request_url


def aws_login(event, context):
    if 'log_level' in os.environ:
        logger.setLevel(os.environ['log_level'])
    logger.debug(event)

    url = aws_signin_url(
        event['queryStringParameters'].get('key_id'),
        event['queryStringParameters'].get('display_name')
    )
    response = {
        "statusCode": 200,
        "body": json.dumps({
            'url': url
        })
    }

    return response


if __name__ == "__main__":  # local debug
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
    console.setFormatter(formatter)
    logger.addHandler(console)
    os.environ['credential_bucket'] = 'personal-aws-credentials'
    os.environ['credential_key'] = 'credentials_config.json'
    os.environ['log_level'] = 'DEBUG'
    test_event = {
        "queryStringParameters": {
            "key_id": 'AKIAIJO4TS44V4Y6SJNA',
            "display_name": "edu1"
        },
    }

    resp = aws_login(test_event, None)
    print(resp)
