#!/bin/bash

version='v1'

export PROJECT_ID='market-navigator-281018'

docker build -t gcr.io/${PROJECT_ID}/market_navigator_analysis:${version} .
docker push gcr.io/${PROJECT_ID}/market_navigator_analysis:v1
