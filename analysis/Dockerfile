FROM python:3.8-slim-buster

# Supress warnings
ARG DEBIAN_FRONTEND=noninteractive
ARG APT_KEY_DONT_WARN_ON_DANGEROUS_USAGE=1

# Various build arguments
ARG BUILD_COMMIT=unknown
ARG BUILD_TIME=unknown
LABEL url-shortener.version=${BUILD_COMMIT} \
      url-shortener.build-time=${BUILD_TIME}

# Source code
WORKDIR /usr/src/app

# Directory where bucket will be mounted
RUN mkdir -p /data/market_navigator/static_data

# Reference: https://runnable.com/blog/9-common-dockerfile-mistakes
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      curl gnupg2 git && \
    rm -rf /var/lib/apt/lists/*

# Prepare GCSFuse installation: https://www.opcito.com/blogs/Introduction-to-persistent-volumes-and-mounting-gcp-buckets-on-containers/
RUN echo "deb http://packages.cloud.google.com/apt gcsfuse-jessie main" \
      | tee /etc/apt/sources.list.d/gcsfuse.list && \
    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add -

RUN apt-get update && apt-get install -y --no-install-recommends gcsfuse

COPY src/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt --no-binary :all

# Copies the code into the work directory above
COPY src /usr/src/app/
