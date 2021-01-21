#!/usr/bin/env bash
while true
do
    python manage.py update_feeds
    sleep 10
done
