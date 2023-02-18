.PHONY: help, ci-black, ci-flake8, ci-test, isort, black, docs, dev-start, dev-stop

## Ensure this is the same name as in docker-compose.yml file
CONTAINER_NAME="spotify_slack_voting_develop_${USER}"
PROJECT=spotify_slack_voting
API_PROJ_NAME=spotify_slack_voting
PROJ_DIR="/mnt/spotify_slack_voting"
COMPOSE_FILE=docker/docker-compose.yml
DEV_SERVICE=develop

# takes advantage of the makefile structure (command; ## documentation)
# to generate help
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

git-tag:  ## Tag in git, then push tag up to origin
	git tag $(TAG)
	git push origin $(TAG)


ci-black: dev-start ## Test lint compliance using black. Config in pyproject.toml file
	docker exec -t $(CONTAINER_NAME) black --check $(PROJ_DIR)


ci-isort: dev-start ## Test lint compliance using black. Config in pyproject.toml file
	docker exec -t $(CONTAINER_NAME) isort $(PROJ_DIR) --profile black --check


ci-flake8: dev-start ## Test lint compliance using flake8. Config in tox.ini file
	docker exec -t $(CONTAINER_NAME) flake8 $(PROJ_DIR)


ci-test: dev-start ## Runs unit tests using pytest
	docker exec -t $(CONTAINER_NAME) pytest $(PROJ_DIR)


ci-test-interactive: dev-start ## Runs unit tests with interactive IPDB session at the first failure
	docker exec -it $(CONTAINER_NAME) pytest $(PROJ_DIR)  -x --pdb --pdbcls=IPython.terminal.debugger:Pdb


ci-mypy: dev-start ## Runs mypy type checker
	docker exec -t $(CONTAINER_NAME) mypy --ignore-missing-imports --show-error-codes $(PROJ_DIR)


ci: ci-isort ci-black ci-flake8 ci-mypy ci-test ## Check isort, black, flake8, mypy, and run unit tests
	@echo "CI successful"


isort: dev-start ## Runs isort to sorts imports
	docker exec -t $(CONTAINER_NAME) isort -rc $(PROJ_DIR) --profile black


black: dev-start ## Runs black auto-linter
	docker exec -t $(CONTAINER_NAME) black $(PROJ_DIR)


format: isort black ## Formats repo by running black and isort on all files
	@echo "Formatting complete"


lint: format ## Deprecated. Here to support old workflow


dev-start: ## Primary make command for devs, spins up containers
	docker-compose -f $(COMPOSE_FILE) --project-name $(PROJECT) up -d --no-recreate $(DEV_SERVICE)


dev-stop: ## Spin down active containers
	docker-compose -f $(COMPOSE_FILE) --project-name $(PROJECT) down

# Useful when Dockerfile/requirements are updated)
dev-rebuild: ## Rebuild images for dev containers
	docker-compose -f $(COMPOSE_FILE) --project-name $(PROJECT) up -d --build $(DEV_SERVICE)

bash: dev-start ## Provides an interactive bash shell in the container
	docker exec -it $(CONTAINER_NAME) bash

ipython: dev-start ## Provides an interactive ipython prompt
	docker exec -it $(CONTAINER_NAME) ipython

clean: ## Clean out temp/compiled python files
	find . -name __pycache__ -delete
	find . -name "*.pyc" -delete
