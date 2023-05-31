FROM python:3.11.3-slim-buster

# Install lame
RUN apt-get update && apt-get install -y lame

# switch working directory
WORKDIR /app

# copy the requirements file into the image
COPY ./requirements.txt /app/requirements.txt

# install the dependencies and packages in the requirements file
RUN pip install --no-cache-dir -r requirements.txt

# copy every content from the local directory to the image
COPY . /app