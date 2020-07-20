# If nothing was specified, show help
.PHONY: help
# Based on https://gist.github.com/rcmachado/af3db315e31383502660
## Display this help text.
help:/
	$(info Available targets)
	$(info -----------------)
	@awk '/^[a-zA-Z\-\_0-9]+:/ { \
		helpMessage = match(lastLine, /^## (.*)/); \
		helpCommand = substr($$1, 0, index($$1, ":")-1); \
		if (helpMessage) { \
			helpMessage = substr(lastLine, RSTART + 3, RLENGTH); \
			gsub(/##/, "\n                                     ", helpMessage); \
			printf "%-35s - %s\n", helpCommand, helpMessage; \
			lastLine = "" \
		} \
	} \
	{ hasComment = match(lastLine, /^## (.*)/); \
          if(hasComment) { \
            lastLine=lastLine$$0; \
	  } \
          else { \
	    lastLine = $$0 \
          } \
        }' $(MAKEFILE_LIST)

# Google Container Registry Parameters
GCR_HOSTNAME := gcr.io
PROJECT_ID := market-navigator-281018

####### General #######
.PHONY: format_build_args
format_build_args:
	$(eval BUILD_COMMIT:=$(shell git rev-parse --short HEAD))
	$(eval BUILD_TIME:=$(shell date -u '+%Y-%m-%dT%H:%M:%SZ'))

####### GCP #######

.PHONY: gcr_list_images
gcr_list_images:
	gcloud container images list-tags

####### Kubernetes #######

.PHONY: kube_create_all
kube_create_all:
	kubectl create -f .

####### API #######

.PHONY: api_kube_create
api_kube_create:
	kubectl create -f api

.PHONY: api_kube_delete
api_kube_delete:
	kubectl delete deployment api | true
	kubectl delete service api | true

.PHONY: api_build_docker
api_build_docker: format_build_args
	$(eval IMAGE:=market_navigator_api)

	eval $$(minikube -p minikube docker-env) && \
	docker build \
		--build-arg BUILD_COMMIT=$(BUILD_COMMIT) \
		--build-arg BUILD_TIME=$(BUILD_TIME) \
		--file api/Dockerfile \
		./api \
		-t $(GCR_HOSTNAME)/$(PROJECT_ID)/$(IMAGE):$(BUILD_COMMIT) && \
	docker tag $(GCR_HOSTNAME)/$(PROJECT_ID)/$(IMAGE):$(BUILD_COMMIT) $(GCR_HOSTNAME)/$(PROJECT_ID)/$(IMAGE):latest

.PHONY: api_push_docker
api_push_docker: api_build_docker
		eval $$(minikube docker-env) && \
		docker push $(GCR_HOSTNAME)/$(PROJECT_ID)/$(IMAGE):latest

####### Analysis #######

.PHONY: analysis_kube_create
analysis_kube_create:
	kubectl create -f analysis

.PHONY: analysis_job_delete
analysis_job_delete:
	kubectl delete cronjob analysis

.PHONY: analysis_docker_build
analysis_build_docker: format_date
	export IMAGE='market_navigator_analysis'
	docker build -t $(GCR_HOSTNAME)/$(PROJECT_ID)/${IMAGE}:${DATE} .
	# docker push gcr.io/${PROJECT_ID}/market_navigator_analysis:v1
