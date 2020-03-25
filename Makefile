# The binary to build (just the basename).
MODULE := azure_cis_scanner

# Where to push the docker image. ?= only has ab effect if REGISTRY is not set
REGISTRY ?= gcr.io/develop-x-234400/github.com/kbroughton/azure_cis_scanner

IMAGE := $(REGISTRY)/$(MODULE)

# This version-strategy uses git tags to set the version string
TAG := $(shell git describe --tags --always --dirty)

build-dev:
	@echo "\n${BLUE}Building Development image with labels:\n"
	@echo "name: $(MODULE)"
	@echo "version: $(TAG)${NC}\n"
	@sed                                 \
		-e 's|{NAME}|$(MODULE)|g'        \
		-e 's|{VERSION}|$(TAG)|g'        \
	dev.Dockerfile | docker build -t $(IMAGE):$(TAG) -f- .
	docker tag $(IMAGE):dev-latest

dev:
	docker build -t $(IMAGE):$(TAG) -f dev.Dockerfile .


# Example: make push VERSION=0.0.2
push: build-prod
    @echo "\n${BLUE}Pushing image to GitHub Docker Registry...${NC}\n"
    @docker push $(IMAGE):$(VERSION)

version:
    @echo $(TAG)

.PHONY: clean image-clean build-prod push test

clean:
    rm -rf .pytest_cache .coverage .pytest_cache coverage.xml

docker-clean:
    @docker system prune -f --filter "label=name=$(MODULE)"
