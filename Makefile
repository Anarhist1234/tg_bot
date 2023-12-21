restart:
	- docker compose --file deploy/prod/docker-compose.yml --project-name ucall-bot stop
	git checkout master
	git pull origin master
	docker compose --file deploy/prod/docker-compose.yml --project-name ucall-bot up -d --build
	echo CHECK container status
