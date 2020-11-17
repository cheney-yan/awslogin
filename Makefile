BASH_ENV := env.sh
SHELL := /bin/bash
.PHONY: DEPLOY

export SENV_APPLICATION=
export SENV_DATE=$(shell date '+%a, %d %b %Y %T %Z')
export STAGE=personal

DEPLOY:
	serverless plugin install  --name serverless-domain-manager && \
	serverless plugin install  --name serverless-python-requirements && \
	serverless plugin install  --name serverless-plugin-log-retention && \
	serverless create_domain --stage ${STAGE} && \
	npm install && \
	SLS_DEBUG=1 serverless deploy --stage ${STAGE}
