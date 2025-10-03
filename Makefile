dotenv:
	cp .env.example .env

build:
	docker compose -f docker-compose.dev.yml build

up:
	docker compose -f docker-compose.dev.yml up

upd:
	docker compose -f docker-compose.dev.yml up -d

down:
	docker compose -f docker-compose.dev.yml down

downv:
	docker compose -f docker-compose.dev.yml down -v