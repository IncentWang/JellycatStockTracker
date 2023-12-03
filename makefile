all: build run

build:
	sudo docker build -t jellycattracker .

run:
	sudo docker run -u root -i -t -d -p 8000:8000 --mount source=sqlite_vol,target=/app/volume_data jellycattracker
