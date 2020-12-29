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

# Google Container Registry Parameters
GCR_HOSTNAME := gcr.io
PROJECT_ID := market-navigator-281018
KEY_FILE := /Users/olshansky/.kube/market-navigator-281018-6606d28522f1.json
DOCKER_PASSWORD_JSON := ~/.kube/market-navigator-281018-128bb21264c6.json
DOCKER_PASSWORD := $(shell cat ${DOCKER_PASSWORD_JSON})

####### General #######

.PHONY: format_build_args
format_build_args:
	$(eval BUILD_COMMIT:=$(shell git rev-parse --short HEAD))
	$(eval BUILD_TIME:=$(shell date -u '+%Y-%m-%dT%H:%M:%SZ'))

####### Minikube #######

.PHONY: maybe_start_docker
maybe_start_docker:
	docker info > /dev/null || open /Applications/Docker.app

.PHONY: minikube_start_dashboard
minikube_start_dashboard:
	nohup minikube dashboard &> /dev/null &

.PHONY: minikube_start_with_mount
## MK: Start minikube with a local mount.
minikube_start_with_mount:
	# minikube start --mount-string "$(PWD):/src/" --mount --driver=docker
	minikube start --mount-string "$(PWD):/src/" --mount
	minikube addons enable gcp-auth

####### GCP #######

.PHONY: make_all_volumes
## Volumes: Start all the PVs and PVCs.
make_all_volumes:
	kubectl create -f volumes

.PHONY: gcr_list_images
## GCP: List all images in GCR.
gcr_list_images:
	gcloud container images list-tags

.PHONY: gcloud_auth_docker
## GCP: Authenticate docker related things.
gcloud_auth_docker:
	gcloud auth login
	gcloud config set project $(PROJECT_ID)
	gcloud auth activate-service-account olshansky-daniel-gmail-com@market-navigator-281018.iam.gserviceaccount.com --key-file=$(KEY_FILE)
	gcloud auth configure-docker
	kubectl create secret docker-registry gcr-json-key \
          --docker-server=https://gcr.io \
          --docker-username=_json_key \
          --docker-password='$(DOCKER_PASSWORD)' \
          --docker-email=olshansky.daniel@gmail.com
	kubectl patch serviceaccount default \
          -p '{"imagePullSecrets": [{"name": "gcr-json-key"}]}'

# Aims to use the free tier: https://github.com/Neutrollized/free-tier-gke
# Free tiers can be found here: https://cloud.google.com/free
# This should be cheap ($5/month?)
.PHONY: gcloud_create_cluster
## Create a small kube cluster with the proper permissions.
gcloud_create_cluster:
	gcloud container clusters create market-navigator \
	--zone us-west1-a \
	--node-locations us-west1-a \
	--scopes=default,bigquery,cloud-platform,compute-rw,datastore,storage-full,taskqueue,userinfo-email,sql-admin \
	--machine-type=e2-small \
	--max-nodes=1 \
	--num-nodes=1

.PHONY: gcloud_create_cluster_medium
## Create a medium kube cluster with the proper permissions.
gcloud_create_cluster_medium:
	gcloud container clusters create market-navigator \
	--zone us-west1-a \
	--node-locations us-west1-a \
	--scopes=default,bigquery,cloud-platform,compute-rw,datastore,storage-full,taskqueue,userinfo-email,sql-admin \
	--machine-type=e2-medium \
	--max-nodes=1 \
	--num-nodes=1

.PHONY: gcloud_get_creds
## Get GKE credentials for the cluster.
gcloud_get_creds:
	gcloud container clusters get-credentials market-navigator --zone us-west1-a

####### API #######

.PHONY: api_kube_create
## API: Create all API Kubernetes workloads.
api_kube_create:
	kubectl create -f api

.PHONY: api_docker_push
## API: Delete all API Kubernetes workloads.
api_kube_delete:
	kubectl delete deployment api | true
	kubectl delete service api | true

.PHONY: api_docker_build
## API: Build API docker image.
api_docker_build: format_build_args
	$(eval IMAGE:=market_navigator_api)

	eval $$(minikube -p minikube docker-env) && \
	docker build \
		--build-arg BUILD_COMMIT=$(BUILD_COMMIT) \
		--build-arg BUILD_TIME=$(BUILD_TIME) \
		--file api/Dockerfile \
		./api \
		-t $(GCR_HOSTNAME)/$(PROJECT_ID)/$(IMAGE):$(BUILD_COMMIT) && \
	docker tag $(GCR_HOSTNAME)/$(PROJECT_ID)/$(IMAGE):$(BUILD_COMMIT) $(GCR_HOSTNAME)/$(PROJECT_ID)/$(IMAGE):latest

.PHONY: api_docker_push
## API - Push API docker image.
api_docker_push:
	$(eval IMAGE:=market_navigator_api)
	eval $$(minikube docker-env) && \
		docker push $(GCR_HOSTNAME)/$(PROJECT_ID)/$(IMAGE):latest

####### Analysis #######

.PHONY: analysis_kube_create_cf
## Create the configmap for the analysis job
analysis_kube_create_cf:
	kubectl apply -f analysis/configmap.yaml

.PHONY: analysis_kube_create_job
## Delete the analysis cron job config, create a new one, and trigger a job.
analysis_kube_create_job: analysis_kube_create_cf
	kubectl delete cronjob analysis || sleep 2 \
		&& kubectl create -f analysis/cronjob.yaml \
		&& sleep 2 \
		&& kubectl create job --from=cronjob/analysis analysis-test

.PHONY: analysis_kube_create_job_local
## Delete the analysis cron job config, create a new one, and trigger a job.
analysis_kube_create_job_local: analysis_kube_create_cf
	kubectl delete cronjob analysis || sleep 2 \
		&& kubectl create -f analysis/cronjob-local.yaml \
		&& sleep 2 \
		&& kubectl create job --from=cronjob/analysis analysis-test

.PHONY: analysis_kube_restart_job
## Delete and restart a single instance of the analysis job.
analysis_kube_restart_test_job:
	kubectl delete job analysis-test || sleep 2 \
		&& kubectl create job --from=cronjob/analysis analysis-test

.PHONY: analysis_kube_create
## Analysis: Create all Analysis Kubernetes workloads.
analysis_kube_create:
	kubectl create -f analysis

.PHONY: analysis_job_delete
## Analysis: Delete all Analysis Kubernetes workloads.
analysis_job_delete:
	kubectl delete cronjob analysis

.PHONY: analysis_run
## Analysis: Run a single job.
analysis_run:
	# Dash is included to skip over errors
	-kubectl delete job analysis-test;
	kubectl create job --from=cronjob/analysis analysis-test;

.PHONY: analysis_docker_build
## Analysis: Build Analysis docker image.
analysis_docker_build: format_build_args
	$(eval IMAGE:=market_navigator_analysis)

	eval $$(minikube -p minikube docker-env) && \
	docker build \
		--build-arg BUILD_COMMIT=$(BUILD_COMMIT) \
		--build-arg BUILD_TIME=$(BUILD_TIME) \
		--file analysis/Dockerfile \
		./analysis \
		-t $(GCR_HOSTNAME)/$(PROJECT_ID)/$(IMAGE):$(BUILD_COMMIT) && \
	docker tag $(GCR_HOSTNAME)/$(PROJECT_ID)/$(IMAGE):$(BUILD_COMMIT) $(GCR_HOSTNAME)/$(PROJECT_ID)/$(IMAGE):latest

.PHONY: analysis_docker_push
## Analysis: Push Analysis docker image.
analysis_docker_push:
	$(eval IMAGE:=market_navigator_analysis)
	eval $$(minikube docker-env) && \
		docker push $(GCR_HOSTNAME)/$(PROJECT_ID)/$(IMAGE):latest

####### Chrome Extension #######

.PHONY: chrome_extension_zip
## Zip up the chrome extension
chrome_extension_zip:
	zip -r market_navigator.zip chrome_extension
