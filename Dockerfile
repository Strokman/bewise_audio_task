FROM python:3.11.3-slim-buster

# Compile and install ffmpeg from source
RUN apt-get install lame

# switch working directory
WORKDIR /app

# copy the requirements file into the image
COPY ./requirements.txt /app/requirements.txt

# install the dependencies and packages in the requirements file --no-cache-dir -r
RUN pip install -r requirements.txt

# copy every content from the local directory to the image
COPY . /app