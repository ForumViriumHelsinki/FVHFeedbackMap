# pull base image
FROM python:3.11-slim-bullseye

# set work directory
WORKDIR /app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1


# install dependencies
RUN apt-get update; apt-get install -y netcat postgresql-client gdal-bin python3-gdal

RUN pip install pipenv

# copy Pipfile
COPY Pipfile /app/
COPY Pipfile.lock /app/
RUN pipenv install --system --deploy

# run entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]
