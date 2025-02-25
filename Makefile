.PHONY: build up down restart logs shell prune pull stop start 

# Build and start the containers
build:
	docker-compose up --build -d

# Start the containers without rebuilding
up:
	docker-compose up -d

# Stop and remove the containers
down:
	docker-compose down

# Restart the containers
restart: down up

# Show logs (follow live updates)
logs:
	docker-compose logs -f

# Open a shell inside the email analyzer container
shell:
	docker exec -it email-analyzer bash

# Remove all unused images, containers, and networks
prune:
	docker system prune -af --volumes

# Pull latest images
pull:
	docker-compose pull

# Stop the containers without removing them
stop:
	docker-compose stop

# Start stopped containers
start:
	docker-compose start

