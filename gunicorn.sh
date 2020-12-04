#!/bin/sh

gunicorn --worker-class eventlet --workers=1 --threads=1 -b 0.0.0.0:7777   --log-level=debug --timeout=60 app:app 
