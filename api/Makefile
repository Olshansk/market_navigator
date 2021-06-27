.SILENT:
.PHONY: help

# Reference: https://gist.github.com/rcmachado/af3db315e31383502660

## This help screen

help:
	printf "Available targets\n\n"
	awk '/^[a-zA-Z\-\_0-9]+:/ { \
		helpMessage = match(lastLine, /^## (.*)/); \
		if (helpMessage) { \
			helpCommand = substr($$1, 0, index($$1, ":")-1); \
			helpMessage = substr(lastLine, RSTART + 3, RLENGTH); \
			printf "%-30s %s\n", helpCommand, helpMessage; \
		} \
	} \
	{ lastLine = $$0 }' $(MAKEFILE_LIST)

.PHONY: run_fast_api_server
## Run local API server (https://fastapi.tiangolo.com/)
run_fast_api_server:
	uvicorn main:app --reload

.PHNY: curl_goog_mm
## Curl GOOGL Mayer Multiple Helper
curl_goog_mm:
	curl -X GET localhost:8000/charts/mayer_multiple/GOOGL