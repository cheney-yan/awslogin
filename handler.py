#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import os
import requests
import boto3

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def api_suite(event, context):
  if 'log_level' in os.environ:
    logger.setLevel(os.environ['log_level'])
  logger.debug(event)

  env = os.environ['env']
  user_type = os.environ['user_type']

  token = get_token(env,user_type)
  for path in TEST_SUITE[user_type]:
    endpoint = 'https://' + user_type + 'api.' + env + '.sondersafe.com/main/' + path
    endpoint = f'https://app.{env}.sondersafe.com/{user_type}_api/' + path
    response = call_endpoint(endpoint, token)
    logger.info(response)
    if response['statusCode'] != 200:
      return {"statusCode": response['statusCode'], "body": response['body']}

  return {"statusCode": 200, "body": user_type + ' test suite is successful.'}


def check_stp_endpoint(event, context):
  if 'log_level' in os.environ:
    logger.setLevel(os.environ['log_level'])
  logger.debug(event)

  if 'env' in os.environ:
    env = os.environ['env']

  logger.debug(env)

  path = event.get('path', '/health')
  if path == '/health':
    status_code = 200
    body = 'Service is healthy'
  else:
    _, prefix_path, full_path = path.split('/', 2)  # split into domain,domain_subpath
    if 'stp3_api' != prefix_path:
      logger.error('Prefix path %s is invalid', prefix_path)
      status_code = 400
      body = 'This path is not allowed'
    elif '.sondersafe.com' not in full_path:
      status_code = 400
      body = 'This full path is invalid'
    else:
      if 'member_api' in full_path:
        user_type = 'member'
      elif 'portal_api' in full_path:
        user_type = 'portal'
      elif 'lo_api' in full_path:
        user_type = 'lo'
      else:
        return {"statusCode": 400, "body": 'This full path is invalid'}
      token = get_token(env,user_type)
      logger.debug(full_path)
      response = call_endpoint('https://' + full_path, token)
      status_code = response['statusCode']
      body = response['body']
  return {
    "statusCode": status_code,
    "body": body
  }


def health_check(event, context):
  if 'log_level' in os.environ:
    logger.setLevel(os.environ['log_level'])
  logger.debug(event)

  path = event.get('path', '/health')
  if path == '/health':
    status_code = 200
    body = 'Service is healthy'
  else:
    _, inner_domain, inner_path = path.split('/', 2)  # split into domain,domain_subpath
    if not inner_domain.endswith('.sondersafe.com') and not inner_domain.endswith('.sonderaustralia.com'):
      logger.error('Domain %s must end with .sondersafe.com or .sonderaustralia.com', inner_domain)
      status_code = 400
      body = 'This domain is not allowed'
    elif inner_path is not '' and 'health' not in inner_path:
      status_code = 400
      body = 'This path is not allowed'
    else:
      # try both https and http
      try:
        response = requests.get(
          url=f'https://{inner_domain}/{inner_path}',
          timeout=20
        )
      except Exception as e:
        response = requests.get(
          url=f'http://{inner_domain}/{inner_path}',
          timeout=20
        )
      status_code = response.status_code
      body = response.text
  return {
    "statusCode": status_code,
    "body": body
  }

def call_endpoint(url, token):
    print(url)
    headers = {'Authorization': 'Bearer ' + token}
    response = requests.get(
      url=url,
      headers=headers,
      timeout=20
    )
    status_code = response.status_code
    body = response.text
    return {
      "statusCode": status_code,
      "body": body
    }


def get_token(environment, app):
    client = boto3.client('cognito-idp')
    response = client.admin_initiate_auth(
        UserPoolId=DEFAULT_INFO[environment][app]['UserPoolId'],
        ClientId=DEFAULT_INFO[environment][app]['ClientId'],
        AuthFlow='ADMIN_NO_SRP_AUTH',
        AuthParameters={
            'USERNAME': DEFAULT_INFO[environment][app]['USER_NAME'],
            'PASSWORD': DEFAULT_INFO[environment][app]['PASSWORD']
        },
    )
    return response['AuthenticationResult']['IdToken']

TEST_SUITE = {
  'member':[
    'member/me',
    'member/me/status'
  ],
  'portal':[
    'operator/me',
    'support_case?alarm=1&status=open&size=1&sort=createdAt,asc'
  ]
}

DEFAULT_INFO = {
    'prod': {
        'member': {
            "ClientId": "5r6nj53ogf6s62ivpbnjtf3n9o",
            "UserPoolId": "ap-southeast-2_qAxYSxjBY",
            "USER_NAME": "jenkins@sondersafe.com",
            "PASSWORD": "Abcd1234",
            'API_KEY': "member-feature-630ba3d7-6a7a-4b1c-ad59-413205a549a8"
        },
        'portal': {
            "ClientId": "2a9qqkbj52r9s4e5n7a0mj3krq",
            "UserPoolId": "ap-southeast-2_iX88JUmsO",
            "USER_NAME": "jenkins@sondersafe.com",
            "PASSWORD": "Abcd1234",
            "API_KEY": "portal-feature-600db53d-a432-46f2-8c79-994a36fcca14"
        },
        'lo': {
            "ClientId": "2j8639dtqm5hrk68o8o7m70r85",
            "UserPoolId": "ap-southeast-2_v07JGcZPL",
            "USER_NAME": "jenkins@sondersafe.com",
            "PASSWORD": "Abcd1234",
            "API_KEY": "lo-feature-600db53d-a432-46f2-8c79-994a36fcca14"
        },
        'system': {
            "API_KEY": "xnzFe56tWZ3aGou5L55CS9qfjnZLhYTk72O5ORXR"
        },
    },
    'staging': {
        'member': {
            "ClientId": "11rk7t70bc4rv6hhpfhu6jagmh",
            "UserPoolId": "ap-southeast-2_o2aB4SdTI",
            "USER_NAME": "sonderautomation@gmail.com",
            "PASSWORD": "Abcd1234",
            "API_KEY": "member-feature-630ba3d7-6a7a-4b1c-ad59-413205a549a8"
        },
        'portal': {
            "ClientId": "1u8q84ph0tlg48h0u8e86uo6es",
            "UserPoolId": "ap-southeast-2_LPQw7a8jf",
            "USER_NAME": "sonderoperator@gmail.com",
            "PASSWORD": "Abcd1234",
            "API_KEY": "portal-feature-600db53d-a432-46f2-8c79-994a36fcca14"
        },
        'lo': {
            "ClientId": "7fjo2lakomaji0aq46lk2vsi51",
            "UserPoolId": "ap-southeast-2_snHHPbv4m",
            "USER_NAME": "sonderautomationlo@gmail.com",
            "PASSWORD": "Abcd1234",
            "API_KEY": "lo-feature-600db53d-a432-46f2-8c79-994a36fcca14"
        },
        'system': {
            "API_KEY": "oze9eaWi0Z33PX7qXq0Eh2F3WrIlaI0N40jiLxxm"
        },
    },
    'dev': {
        'member': {
            "ClientId": "1dviuju82j5afg49lm3um9n32c",
            "UserPoolId": "ap-southeast-2_U5n4BJsgb",
            "USER_NAME": "nicholas@sondersafe.com",
            "PASSWORD": "Abcd1234",
            "API_KEY": "member-feature-630ba3d7-6a7a-4b1c-ad59-413205a549a8"
        },
        'portal': {
            "ClientId": "j2bht37kksq5ltaeu3lpkafga",
            "UserPoolId": "ap-southeast-2_Oq8tTrvnv",
            "USER_NAME": "nicholas@sondersafe.com",
            "PASSWORD": "Abcd1234",
            "API_KEY": "portal-feature-600db53d-a432-46f2-8c79-994a36fcca14"
        },
        'lo': {
            "ClientId": "283c58o2of3kddsb427hohf33c",
            "UserPoolId": "ap-southeast-2_AJJpBrS3u",
            "USER_NAME": "nicholas@sondersafe.com",
            "PASSWORD": "Abcd1234",
            "API_KEY": "lo-feature-600db53d-a432-46f2-8c79-994a36fcca14"
        },
        'system': {
            "API_KEY": "5nEPkpFcgI9NKhwOFoXD92WcVf37iz2I81nNNYVm"
        },
    }
}