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

.PHONE: help_periodic_manual_caching
## Periodic cache of historical data
help_periodic_manual_caching:
	@echo "" \
		"GCLOUD commands\n" \
		"\tRecreate the cluster: make gcloud_create_cluster_medium\n" \
		"\tAutheticate: make gcloud_auth_docker\n\n" \
		"Bind the bucket locally:\n" \
		"\tsudo mkdir -p /tmp/data/market_navigator/static_data\n" \
		"\tsudo mkdir /Volumes/GCS/bucket\n" \
		"\tsudo chown -R olshansky /Volumes/GCS/bucket\n" \
		"\tgcsfuse --debug_fuse --debug_gcs --debug_invariants market-navigator-data /Volumes/GCS/bucket\n\n" \
		"Check min max dates:\n" \
		"\tjupyter notebook\n" \
		"\thttp://127.0.0.1:8888/notebooks/Read%20in%20cached%20data.ipynb\n\n" \
		"Trigger the job::\n" \
		"\tmake analysis_kube_create_job_gke\n\n" \
		"Track costs and usage:\n" \
		"\thttps://iexcloud.io/console/\n" \
		"\thttps://console.cloud.google.com/kubernetes/list?project=market-navigator-281018\n\n" \
		"Delete the cluster:\n" \
		"\tgcloud container clusters delete --zone us-west1-a market-navigator\n" \
		"\tgcloud container clusters list\n\n" \
		"Check and backup new data:\n" \
		"\tVerify the new dates at http://127.0.0.1:8888/notebooks/Read%20in%20cached%20data.ipynb\n" \
		"\tDownload and backup the file from https://console.cloud.google.com/storage/browser/market-navigator-data\n\n" \
		"Debugging commands:\n" \
		"\tsudo diskutil umount force  /Volumes/GCS/bucket\n" \
		"\tgcsfuse --foreground --debug_fuse --debug_gcs --debug_invariants market-navigator-data /Volumes/GCS/bucket\n" \


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

.PHONY: gcloud_create_docker_secret
## Create the kubernetes docker registry secret.
gcloud_create_docker_secret:
	@echo $(DOCKER_PASSWORD)
	kubectl create secret docker-registry gcr-json-key \
		--save-config --dry-run=client \
    --docker-server=https://gcr.io \
    --docker-username=_json_key \
    --docker-password='$(DOCKER_PASSWORD)' \
    --docker-email=olshansky.daniel@gmail.com \
		-o yaml | kubectl apply -f -

.PHONY: gcloud_create_gcp_key
## Create the kubernetes GCP secret.
gcloud_create_gcp_key:
	kubectl create secret generic gcp-key \
		--save-config --dry-run=client \
		--from-file=$(KEY_FILE) \
		-o yaml | kubectl apply -f -

.PHONY: gcloud_secrets
## Create all the kubernetes secrets.
gcloud_secrets: gcloud_create_gcp_key gcloud_create_docker_secret

.PHONY: gcloud_auth_docker
## GCP: Authenticate docker related things.
gcloud_auth_docker: gcloud_create_docker_secret
	gcloud auth login
	gcloud config set project $(PROJECT_ID)
	gcloud auth activate-service-account olshansky-daniel-gmail-com@market-navigator-281018.iam.gserviceaccount.com --key-file=$(KEY_FILE)
	gcloud auth configure-docker
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

####### Analysis #######

.PHONY: analysis_kube_create_cf
## Create the configmap for the analysis job
analysis_kube_create_cf:
	kubectl apply -f analysis/configmap.yaml

.PHONY: analysis_kube_create_job
## GKE: Delete the analysis cron job config, create a new one, and trigger a job.
analysis_kube_create_job_gke: analysis_kube_create_cf
	kubectl delete cronjob analysis || sleep 2 \
		&& kubectl create -f analysis/cronjob-gke.yaml \
		&& sleep 2 \
		&& kubectl create job --from=cronjob/analysis analysis-test

.PHONY: analysis_kube_create_job_digital_ocean
## Digital Ocean: Delete the analysis cron job config, create a new one, and trigger a job.
analysis_kube_create_job_digital_ocean: gcloud_secrets analysis_kube_create_cf
	kubectl delete cronjob analysis || sleep 2 \
		&& kubectl create -f analysis/cronjob-digital-ocean.yaml \
		&& sleep 2 \
		&& kubectl create job --from=cronjob/analysis analysis-test

.PHONY: analysis_kube_create_job_minikube
## Minikube: Delete the analysis cron job config, create a new one, and trigger a job.
analysis_kube_create_job_minikube: analysis_kube_create_cf
	kubectl delete cronjob analysis || sleep 2 \
		&& kubectl create -f analysis/cronjob-minikube.yaml \
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
	zip -r market_navigator.zip chrome_extension/extension
