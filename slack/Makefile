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
	uvicorn app:api --reload --port 3000 --log-level warning

.PHONY: configure_slash_commands_url
## Echo the link required to update local development
	@echo "https://api.slack.com/apps/A0270GW121Y/slash-commands?"