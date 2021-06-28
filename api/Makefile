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

.PHONY: curl_goog_mm
## Curl GOOGL Mayer Multiple Helper
curl_goog_mm:
	curl -X GET localhost:8000/charts/mayer_multiple/GOOGL

.PHONY: get_bucket_policy
## Get bucket policy for cdn.olshansky.info
get_bucket_policy:
	aws s3api get-bucket-policy --bucket cdn.olshansky.info

.PHONY: get_bucket_policy
## Get bucket policy for cdn.olshansky.info
get_bucket_policy:
	aws s3api get-bucket-policy --bucket cdn.olshansky.info > /tmp/cdn_olshansky_info_policy.json
	@echo "see /tmp/cdn_olshansky_info_policy.json"

.PHONY: put_bucket_policy
## Put bucket policy for cdn.olshansky.info
put_bucket_policy:
	aws s3api put-bucket-policy --bucket cdn.olshansky.info --policy file://cdn_olshansky_info_policy.json

.PHONY: get_bucket_lifecycle
## Get bucket lifecycle for cdn.olshansky.info
get_bucket_lifecycle:
	aws s3api get-bucket-lifecycle --bucket cdn.olshansky.info

.PHONY: put_bucket_lifecycle
## Put bucket policy for cdn.olshansky.info
put_bucket_lifecycle:
	aws s3api put-bucket-lifecycle-configuration --bucket my-bucket --lifecycle-configuration  file://lifecycle.json
