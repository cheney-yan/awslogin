FROM alpine
LABEL maintainer="cheney.yan@gmail.com"
ADD app /app
RUN apk update \
    && apk add --virtual build-dependencies \
    build-base \
    gcc \
    wget \
    git \
    && apk add \
    bash
RUN apk add python3-dev libressl-dev libffi-dev \
    && pip3 install --upgrade 'pip==9.0.3' \
    && pip3 install -r /app/requirements.txt

WORKDIR /app
ENTRYPOINT [ "python3" ]
CMD [ "app.py" ]
