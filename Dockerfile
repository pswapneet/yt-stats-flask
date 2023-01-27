#
# NOTE! THIS FILE CREATED AT 5:AM!
#
# DO NOT USE IT WILL NOT WORK!
#
#FROM python:3.8.16-alpine

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
#RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    python3-dev \
    libssl-dev \
    libffi-dev \
    python3-pip

# copy requirements file
COPY requirements.txt .

# install requirements
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

# copy project files
# COPY . .

# start app
# CMD ["flask", "run", "--host=0.0.0.0"]