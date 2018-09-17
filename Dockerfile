FROM alpine
LABEL maintainer="cheney.yan@gmail.com"
ADD app /app

RUN apk add --no-cache bash python3 \
	&& pip3 install --upgrade 'pip==9.0.3' \
    && pip3 install -r /app/requirements.txt

WORKDIR /app
ENTRYPOINT [ "python3" ]
CMD [ "app.py" ]