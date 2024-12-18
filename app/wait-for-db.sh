#!/bin/bash

set -e

host="$EXTERNAL_DATABASE_URL"
shift
cmd="$@"

until netcat -z "$host" 5432; do
  echo "Waiting for the database at $host:5432..."
  sleep 2
done

echo "Database is up - executing init script"

# Выполняем SQL-скрипт
psql -h "$host" -U "user" -d "postgres_db_av9c" -a -f /path/to/init.sql

echo "SQL script executed successfully"

# Выполняем переданную команду
exec $cmd
