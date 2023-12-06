#!/bin/bash

nohup conda run -n JellycatTrackerEnv gunicorn -b 0.0.0.0:8000 JellycatTracker.wsgi &
nohup conda run -n JellycatTrackerEnv python long_polling_deamon.py &
tail -f /dev/null
