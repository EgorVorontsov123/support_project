#!/bin/bash

set -e

host="$1"
shift
cmd="$@"

until netcat -z "$host" 5432; do
  echo "Waiting for the database at $host:5432..."
  sleep 2
done

echo "Database is up - executing command"
exec $cmd
