all: build run

build:
	sudo docker build -t jellycattracker .
	sudo docker image prune -f
	sudo docker stop jellycattracker || true
	sudo docker container prune -f

run:
	sudo docker run -u root --name jellycattracker -i -t -d -p 8000:8000 --mount source=sqlite_vol,target=/app/volume_data jellycattracker
