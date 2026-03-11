#!/bin/bash
set -e 

echo "Waiting for PostgreSQL..."
while ! python -c "
import socket
s = socket.create_connection(('${DB_HOST:-db}', ${DB_PORT:-5432}), timeout=1)
s.close()
" 2>/dev/null; do
sleep 1 
done 
echo "PostgresSQL is ready."

echo "Running migrations"
.venv/bin/python manage.py migrate --noinput

exec "$@"