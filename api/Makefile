.SILENT:
.PHONY: help

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

.PHONY: fastapi_run_server
## Run local API server (https://fastapi.tiangolo.com/)
fastapi_run_server:
	uvicorn main:app --reload --log-level=debug --host=0.0.0.0 --port=8000

TICKER ?= GOOGL
.PHONY: curl_mm_local
## Curl local MM PNG chart (GOOGL by default)
curl_goog_mm:
	curl -X GET localhost:8000/charts/mayer_multiple/$(TICKER)/png | jq

.PHONY: s3_get_bucket_policy
## Get bucket policy for cdn.olshansky.info
s3_get_bucket_policy:
	aws s3api get-bucket-policy --bucket cdn.olshansky.info

.PHONY: s3_get_bucket_policy_to_json
## Get bucket policy for cdn.olshansky.info
s3_get_bucket_policy_to_json:
	aws s3api get-bucket-policy --bucket cdn.olshansky.info > /tmp/cdn_olshansky_info_policy.json
	@echo "see /tmp/cdn_olshansky_info_policy.json"

.PHONY: s3_put_bucket_policy
## Put bucket policy for cdn.olshansky.info
s3_put_bucket_policy:
	aws s3api put-bucket-policy --bucket cdn.olshansky.info --policy file://cdn_olshansky_info_policy.json

.PHONY: s3_get_bucket_lifecycle
## Get bucket lifecycle for cdn.olshansky.info
s3_get_bucket_lifecycle:
	aws s3api get-bucket-lifecycle --bucket cdn.olshansky.info

.PHONY: s3_put_bucket_lifecycle
## Put bucket policy for cdn.olshansky.info
s3_put_bucket_lifecycle:
	aws s3api put-bucket-lifecycle-configuration --bucket my-bucket --lifecycle-configuration  file://lifecycle.json

.PHONY: quandl_recompute
## Hardcoded paths to CSV paths on SD card to recompute daily data used for processing
quandl_recompute:
	python data/writer.py recompute --output_dir=/Volumes/SDCard/Quandl --sharadar_daily_path=/Volumes/SDCard/Quandl/SHARADAR_DAILY.csv --sharadar_sep_path=/Volumes/SDCard/Quandl/SHARADAR_SEP.csv

.PHONY: quandl_append
## Hardcoded paths to append data to daily data on SD card
quandl_append:
	python data/writer.py append --daily_data_path=/Volumes/SDCard/Quandl/daily_data.feather

.PHONY: quandl_download
## Hardcoded paths to append data to daily data on SD card
quandl_download:
	python data/reader.py download --output_dir=/Volumes/SDCard/

.PHONY: kubectl_argo_local
## Local port forwarding to use argo with minikube for development
kubectl_argo_local:
	@echo "https://localhost:2746"
	kubectl -n argo port-forward deployment/argo-server 2746:2746

.PHONY: kubectl_argo_remote
## Remote port forwarding to use argo with minikube for development
kubectl_argo_remote:
	@echo "https://127.0.0.1:2746"
	kubectl -n argo port-forward --address 0.0.0.0 svc/argo-server 2746:2746 > /dev/null &

.PHONY: python_format
## All the python formatting
python_format:
	autoflake .
	black .
	isort .

