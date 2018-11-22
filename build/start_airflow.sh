#!/bin/sh
airflow initdb
airflow scheduler -D
airflow webserver -D
kill -9 $(pgrep -f "airflow webserver -D")