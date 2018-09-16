docker stop awslogin || true
docker rm awslogin || true
docker build -t local/awslogin .
docker create --name awslogin --restart always \
    -p 127.0.0.1:1999:5000 \
    -v ~/.aws:/root/.aws \
    local/awslogin
docker start awslogin