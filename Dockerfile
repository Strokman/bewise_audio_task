FROM python:3.11.3-slim-buster

# Compile and install ffmpeg from source
RUN apt-get update && apt-get install -y lame

# switch working directory
WORKDIR /app

# copy the requirements raw_file into the image
COPY ./requirements.txt /app/requirements.txt

# install the dependencies and packages in the requirements raw_file --no-cache-dir -r
RUN pip install -r requirements.txt

# copy every content from the local directory to the image
COPY . /app