# pull official base image
FROM python:3.11-slim-bullseye

# set working directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# install system dependencies
RUN apt-get update \
  && apt-get -y install netcat gcc postgresql libgl1-mesa-glx libglib2.0-0 libsm6 libxrender1 libxext6 entr\
  && apt-get clean

# install python dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# add app
COPY . .
