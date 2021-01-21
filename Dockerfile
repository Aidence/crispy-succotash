FROM python:3.8-alpine
RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev bash
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
ADD . /code/
RUN pip install -r requirements.txt
EXPOSE 8000
