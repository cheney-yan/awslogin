#!/usr/bin/env python
from flask import Flask, redirect, request
import json
import os
import urllib
import boto3
import requests
import botocore
import configparser

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


def aws_signin_url(base_profile, session_name=None, assumed_role=None, time_to_live=None):
    session = boto3.Session(profile_name=base_profile)
    sts_client = session.client('sts')
    if not assumed_role:  # using the profile directly
        if not time_to_live:
            time_to_live = 129600
        else:
            time_to_live = int(time_to_live)
        credentials = sts_client.get_federation_token(
            Name=session_name,
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
            RoleSessionName=session_name
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
    signin_token = json.loads(r.text)

    # Create URL where users can use the sign-in token to sign in to
    # the console. This URL must be used within 15 minutes after the
    # sign-in token was issued.
    request_parameters = '?Action=login&Issuer={issuer}&Destination={destination}&SigninToken={signin_token}'.format(
        issuer=session_name,
        destination=urllib.parse.quote("https://console.aws.amazon.com/"),
        signin_token=signin_token["SigninToken"]
    )
    request_url = "https://signin.aws.amazon.com/federation" + request_parameters

    return request_url


app = Flask(__name__)


@app.route('/awslogin', methods=['GET'])
def awslogin():
    try:
        profile = request.args.get('profile', 'prod-syd-role')
        config = configparser.ConfigParser()
        config.read(os.path.expanduser('~/.aws/credentials'))
        if profile not in config._sections.keys():
            return "Unknown profile", 500
        try:
            source_profile = config.get(profile, 'source_profile')
            # it has a source profile
            role = config.get(profile, 'role_arn')
            url = aws_signin_url(base_profile=source_profile, session_name="Assumed", assumed_role=role)
        except:  # this is already root
            url = aws_signin_url(base_profile=profile,
                                 session_name=profile)

        format = request.args.get('format', '')
        if format.lower() == 'txt':
            return url
        else:
            return redirect(url)
    except botocore.exceptions.ClientError as e:
        if "session credentials" in e.response['Error'].get('Message'):
            return "ERROR: You probably are using a assumed role profile. Base profile must be of static (IAM user) identity.", 400
    except Exception as e:
        return str(e), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0')
