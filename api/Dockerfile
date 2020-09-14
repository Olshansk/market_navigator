FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

ARG BUILD_COMMIT=unknown
ARG BUILD_TIME=unknown
LABEL url-shortener.version=${BUILD_COMMIT} \
      url-shortener.build-time=${BUILD_TIME}

WORKDIR /usr/src/app
