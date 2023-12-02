#!/bin/bash

nohup conda run -n JellycatTrackerEnv python manage.py runserver 0.0.0.0:8000 &
nohup conda run -n JellycatTrackerEnv python long_polling_deamon.py &
tail -f /dev/null