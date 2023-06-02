#!/bin/sh

DIR="postgres-data"
if [ -d "$DIR" ]; then
  echo "${DIR} exists"
else
 mkdir postgres-data
fi

docker-compose up --build