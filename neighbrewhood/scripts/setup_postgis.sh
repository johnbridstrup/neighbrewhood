#!/bin/bash

sudo apt install gdal-bin libgdal-dev -y 
sudo apt install python3-gdal -y
sudo apt install binutils libproj-dev -y

docker run -d --name postgis_postgres \
    -e POSTGRES_db=gis \
    -e POSTGRES_PASSWORD=123456789 \
    -e POSTGRES_USER=user001  \
    -v /tmp \
    -p 5432:5432 \
    kartoza/postgis:16-3.4--v2023.11.04
