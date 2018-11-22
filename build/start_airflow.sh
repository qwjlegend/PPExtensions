#!/bin/sh
airflow initdb
nohup airflow scheduler -D &
nohup airflow webserver -D &
