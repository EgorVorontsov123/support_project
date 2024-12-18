#!/bin/bash

set -e

host="$DATABASE_HOST"
shift
cmd="$@"

until netcat -z "$host" 5432; do
  echo "Waiting for the database at $host:5432..."
  sleep 2
done

echo "Database is up - executing init script"

# Выполняем SQL-скрипт
psql -h "$host" -U "user" -d "postgres_db_av9c" -a -f ./init.sql:/docker-entrypoint-initdb.d/init.sql

echo "SQL script executed successfully"

# Выполняем переданную команду
exec $cmd
