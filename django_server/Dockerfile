# pull base image
FROM python:3.11-slim-bullseye

# set work directory
WORKDIR /app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# copy Pipfile
COPY Pipfile /app/
COPY Pipfile.lock /app/

# install dependencies
RUN apt-get update; apt-get install -y netcat
# If you need GeoDjango:
RUN apt-get install -y gdal-bin python3-gdal
RUN pip install pipenv
RUN pipenv install --system --deploy
RUN apt-get install -y postgresql-client

# run entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]
