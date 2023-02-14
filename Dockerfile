# pull official base image
FROM python:3.9.6-alpine

# set work directory
WORKDIR /usr/src/all_messages

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apk update \
    && apk add postgresql-dev gcc python3-dev musl-dev

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY ./entrypoint.sh .
RUN sed -i 's/\r$//g' /usr/src/all_messages/entrypoint.sh
RUN chmod +x /usr/src/all_messages/entrypoint.sh

# copy project
COPY . .

ENTRYPOINT ["/usr/src/all_messages/entrypoint.sh"]
