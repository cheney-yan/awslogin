# awslogin
Generate AWS Web Console login url from your aws credentials profile. Avoid using Username/Passowrd/2FA token.


# Usage
This tool uses AWS GetSigninToken interface to generate an URL to login to AWS management console. The theory can be found in the AWS DOCO https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_providers_enable-console-custom-url.html.

## Quick start

Assume your aws credentials are stored under `~/.aws/` directory, with content

```
[base_profile]
aws_secret_access_key=qvhiPEi...N8m2IyOfzg8
aws_access_key_id=AK...DGQ
region = ap-southeast-2
```
You can simply run the service in the following command

```
docker run --name awslogin --restart always \
    -p 127.0.0.1:1999:5000 \
    -v ~/.aws:/root/.aws \
    cheneyyan/awslogin
```

Then access it using your browser:
```
http://localhost:1999/awslogin?baseProfile=base_profile
```
your browser will be forwarded to logged in session with based on the credential base_profile.

Then access it using your browser:
```
http://localhost:1999/awslogin?baseProfile=base_profile&roleArn=arn:aws:iam::551423894163:role%2Fadmin
```
your browser will be forwarded to logged in session with based on the role `role_arn=arn:aws:iam::551423894163:role/admin`, given the IAM credential for base_profile are allowed to assume to this role.



## Why this tool
- I am lazy, I guess. I don't wnat to type in my user name, (the super strong)password and pull out of my mobile for 2FA token every time I'm logging in.
- As a developer, I access multiple AWS account at the same time, and I most of the time I'd like work in parallel with these accounts. You can only sign in one same account at the same time.
- The officieal profile switching solution is painful.

## How this tool works
This tool works as a local http server. On request:
```
http://localhost:1999/awslogin?baseProfile=base_profile
```
It respond with 
```
HTTP/1.0 302 FOUND
Content-Type: text/html; charset=utf-8
Content-Length: 2113
Location: https://signin.aws.amazon.com/federation?Action=login&Issuer=base_profile&Destination=https%3A//console.aws.amazon.com/&SigninToken=61ytivt40YMae3j-pmfy_4kaOMtkG_bbq8jVfxX...
Server: Werkzeug/0.14.1 Python/3.6.6
Date: Sun, 16 Sep 2018 01:35:49 GMT
```
So that your browser will automatically be forwarded and logged in to AWS. Now you have successully logged in. Your permission is derived from what the `base_profile` profile is allows.

## TTL
You can also specify the expected TTL of the login URL. Besides, AWS also has its own definition of TTL for these links. If not specified, the URLs generated has to be used within 15 mins and login session will expire between 12-36 hours. It also depends on whether your cedentail is IAM or a role. Check AWS documents for exact information.

# Parameters and customization
## Parameters

- baseProfile: Mandatory: The profile name in your local ~/.aws/credential(profile) file. This profile will be used to generate the signed URL. This profile must be an IAM user credential. If you are using an assumed role(including cross account assuming role), you must specify the roleArn parameter.
- roleArn: Optional. When signing a login url from a role, BOTH baseProfile and roleArn parameters are required. The baseProfile is the source_profile that the role relies on. 
- sessionName: Optional: Give it a meaningful name. This name will be appearing on your AWS web console as well as the AWS Cloudtrail.
- ttl: Optional: How long do you want the Login session to be valid.
- format: Optional: only "txt" is supported. It returns only in text format but not 302 url forward response.

NOTE: Encode your parameters carefully, especially the `/` character in roleArn parameter.

## customization

- Port: go to `start-service.sh` file and update the port.
- Debug: If you really need to debug, please DIY by updating the code and execute `start-service-build.sh`

# Use Case
## Bookmark

Just add `http://localhost:1999/awslogin?baseProfile=base_profile` as the link of your bookmark to the AWS account. That simple!

## Customized application

I use `nativefier` to generate customized application for each of the AWS accounts. A good thing for `nativefier` is it generates apps with customized app name as well as ICON. I only have to set the home URL of the app as `http://localhost:1999/awslogin?baseProfile=AWS_PROFILE` and add "amazon.com" as the `internal-url` parameter and that is all done! When login expires in the nativefier application, I simply create a new tab within the application and it automatically jumps to the home URL and which refreshes the local session for amazon.com.

A sample command for creating such application:
```
    nativefier --name "AWS ABCD" --internal-urls "amazon.com" --fast-quit  --disable-dev-tools "$url"
```
Project link: https://github.com/jiahaog/nativefier

# License
MIT.