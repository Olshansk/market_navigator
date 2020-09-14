FROM python:3

ARG BUILD_COMMIT=unknown
ARG BUILD_TIME=unknown
LABEL url-shortener.version=${BUILD_COMMIT} \
      url-shortener.build-time=${BUILD_TIME}

WORKDIR /usr/src/app

COPY src/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
