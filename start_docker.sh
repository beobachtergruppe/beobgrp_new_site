#!/bin/bash

docker build -t beobgrp_site:0.1 .
docker run -p 127.0.0.1:8000:8000 --network host --env WAGTAIL_DB_PASSWORD beobgrp_site:0.1