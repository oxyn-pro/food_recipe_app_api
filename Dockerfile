FROM python:3.9-alpine

ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /requirements.txt

# these dependecies will stay in our docker container
RUN apk add --update --no-cache postgresql-client jpeg-dev

# these build dependencies won't stay in our docker container, these are just dependencies that are required before pip installs(for installing pip packages)
RUN apk add --update --no-cache --virtual .tmp-build-deps \  
    gcc libc-dev linux-headers postgresql-dev musl-dev zlib zlib-dev

RUN pip install -r /requirements.txt
RUN apk del .tmp-build-deps 

RUN mkdir /app
WORKDIR /app
COPY ./app /app 

# we added /web/media directory in container /vol/ because vol(volume) means that it should be shared by other containers as well
RUN mkdir -p /vol/web/media   
# -p means if vol or any directory does not exist in container, then make it
RUN mkdir -p /vol/web/static

RUN adduser -D user

# give permissions of new directories(media, staic) as a main directory(vol) to a new user
RUN chown -R user:user /vol/
# -R means select all sub-directories of vol (web, media)

# it means that the new set owner has permission to do everything with directory, whereas others(not owner) can only read, and execute files
RUN chmod -R 755 /vol/web/

USER user