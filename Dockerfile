FROM python:2.7-alpine

ADD requirements.txt /

RUN apk add --update --virtual .build gcc musl-dev libffi-dev python2-dev openssl-dev tiff-dev jpeg-dev zlib-dev freetype-dev lcms2-dev libwebp-dev tcl-dev tk-dev python2-tkinter linux-headers && pip install -r requirements.txt && apk del .build && apk add openssl tiff jpeg zlib freetype && rm -rf /var/cache/apk/*

# Directories
ADD database/*.py /database/
ADD imagestore/*.py /imagestore/
ADD static /static
ADD templates /templates

# Files
ADD app.py /
ADD settings.py /
ADD .env /
ADD template.png /
ADD key.pem /root/.oci/oci_api_key.pem

EXPOSE 80
CMD [ "python", "-u", "./app.py" ]
