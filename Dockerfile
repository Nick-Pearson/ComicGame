FROM python:2.7-alpine

ADD requirements.txt /

RUN apk add --update --virtual .build gcc musl-dev libffi-dev python2-dev openssl-dev linux-headers && pip install -r requirements.txt && apk del .build && apk add openssl && rm -rf /var/cache/apk/*

# Directories
ADD database/*.py /database/
ADD imagestore/*.py /imagestore/
ADD static /static
ADD templates /templates

# Files
ADD app.py /
ADD settings.py /
ADD .env /
ADD key.pem /root/.oci/oci_api_key.pem

EXPOSE 80
CMD [ "python", "./app.py" ]
