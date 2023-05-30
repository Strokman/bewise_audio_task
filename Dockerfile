FROM python:3.11.3-slim-buster

# Compile and install ffmpeg from source
RUN git clone https://github.com/FFmpeg/FFmpeg /root/ffmpeg && \
    cd /root/ffmpeg && \
    ./configure --enable-nonfree --disable-shared --extra-cflags=-I/usr/local/include && \
    make -j8 && make install -j8

# If you want to add some content to this image because the above takes a LONGGG time to build
ARG CACHEBREAK=1

# switch working directory
WORKDIR /app

# copy the requirements file into the image
COPY ./requirements.txt /app/requirements.txt

# install the dependencies and packages in the requirements file --no-cache-dir -r
RUN pip install -r requirements.txt

# copy every content from the local directory to the image
COPY . /app