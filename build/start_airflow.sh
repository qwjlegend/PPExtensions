#!/bin/sh
airflow initdb
<<<<<<< HEAD
airflow scheduler -D
airflow webserver -D
kill -9 $(pgrep -f "airflow webserver -D")
=======
nohup airflow scheduler -D &
nohup airflow webserver -D &
>>>>>>> master
