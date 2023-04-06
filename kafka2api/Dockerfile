# pull official base image
FROM python:3.11-slim-bullseye as appbase

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update --fix-missing && \
    apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y apt-utils git

# create directory for the app user
ENV HOME=/home/app
RUN mkdir -p $HOME
WORKDIR $HOME

# create the app user
RUN addgroup --system app && adduser --system --group app
RUN chown -R app:app $HOME

RUN pip install --upgrade pip
COPY ./requirements.txt $HOME/requirements.txt
RUN pip install --no-cache-dir -r $HOME/requirements.txt

USER app


# ==============================
FROM appbase as development
# ==============================

COPY requirements-dev.txt $HOME/requirements-dev.txt
RUN pip install --no-cache-dir -r $HOME/requirements-dev.txt \
    && pip install --no-cache-dir pip-tools

ENV DEV_SERVER=1

COPY --chown=app:app . $HOME/

USER app


# ==============================
FROM appbase as production
# ==============================

COPY requirements-prod.txt $HOME/requirements-prod.txt
RUN pip install --no-cache-dir -r $HOME/requirements-prod.txt

COPY --chown=app:app . $HOME/

USER app
