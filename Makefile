.EXPORT_ALL_VARIABLES:
COMPOSE_PROJECT_NAME=crispy

up:
	docker-compose run app python manage.py migrate
	docker-compose up

test:
	docker-compose run app python manage.py test

build:
	docker-compose build

ssh:
	docker-compose run app bash

.PHONY: \
	up \
	test