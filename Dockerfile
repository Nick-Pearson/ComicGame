FROM python:2.7-alpine

RUN apk add --update --virtual .build gcc musl-dev linux-headers

ADD requirements.txt /
RUN pip install -r requirements.txt

RUN apk del .build && rm -rf /var/cache/apk/*

# Directories
ADD database/*.py /database/
ADD imagestore/*.py /imagestore/
ADD static /static
ADD templates /templates

# Files
ADD app.py /
ADD settings.py /
ADD .env /

EXPOSE 80
CMD [ "python", "./app.py" ]
