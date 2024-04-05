#!/bin/sh
docker-compose down
/web_app/build.sh
docker-compose build
docker-compose up