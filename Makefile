help: ## Shows this help
	@echo "$$(grep -h '#\{2\}' $(MAKEFILE_LIST) | sed 's/: #\{2\} /	/' | column -t -s '	')"

install: ## Install requirements
	@[ -n "${VIRTUAL_ENV}" ] || (echo "ERROR: This should be run from a virtualenv" && exit 1)
	pip install -r requirements.txt
	npm install

.PHONY: requirements.txt
requirements.txt: ## Compile requirements.txt
	pip-compile --upgrade --output-file $@ requirements.in

test: ## Run test suite
	coverage run -m unittest test_web
	coverage report --show-missing || true

dev: ## Run the server with a watcher
	nodemon --ext py -x python web.py

docker/assets: ## Build assets/bundles via Docker
	mkdir -p assets/bundles
	docker run --rm -v ${PWD}:/app:rw --workdir /app node:6 /bin/sh -c "npm install && npm run build"

docker/build: ## Build Docker image
	docker build -t rangzen/jinja2-livepreview .

docker/bash: ## Run a shell in the Docker image
	docker run --rm -it -v ${PWD}:/app -p 9797:9797 rangzen/jinja2-livepreview /bin/sh

docker/run: ## Run Docker image
	docker run --rm -v ${PWD}:/app -p 9797:9797 rangzen/jinja2-livepreview

docker/push: ## Publish Docker image to the registry
	docker push rangzen/jinja2-livepreview
