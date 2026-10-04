#!/usr/bin/env bash
# Start a local, throw-away PostgreSQL server for building the handbook.
#
#   handbook/scripts/start_postgres.sh [DATA_DIR]
#
# Creates the cluster on first use, starts it on port 54329 (override with
# HANDBOOK_PG_PORT) and creates the "handbook" database. build.py loads the sample
# data itself, so nothing else is needed. If you already run PostgreSQL elsewhere,
# skip this script and point the build at it with HANDBOOK_PG_DSN instead, using a
# dedicated database: the build wipes that database's public schema.
# Stop the server with: pg_ctl -D DATA_DIR stop
set -euo pipefail

PGBIN="${PGBIN:-$(ls -d /usr/lib/postgresql/*/bin 2>/dev/null | sort -V | tail -n 1)}"
PORT="${HANDBOOK_PG_PORT:-54329}"
DATA="${1:-${HOME}/.handbook-pgdata}"
[ -n "$PGBIN" ] && export PATH="$PGBIN:$PATH"
command -v initdb >/dev/null || { echo "initdb not found; install PostgreSQL 16 or set PGBIN" >&2; exit 1; }

# PostgreSQL refuses to run as root, so as root run the server as the "postgres" user.
as_db_user() {
  if [ "$(id -u)" = "0" ]; then
    su -s /bin/bash postgres -c "PATH='$PATH' $*"
  else
    bash -c "$*"
  fi
}
if [ "$(id -u)" = "0" ]; then
  [ $# -ge 1 ] || DATA=/var/tmp/handbook-pgdata
  mkdir -p "$DATA" && chown postgres "$DATA"
fi

if [ ! -s "$DATA/PG_VERSION" ]; then
  as_db_user "initdb -D '$DATA' -U postgres --auth=trust -E UTF8 >/dev/null"
fi
if ! as_db_user "pg_ctl -D '$DATA' status >/dev/null 2>&1"; then
  as_db_user "pg_ctl -D '$DATA' -l '$DATA/server.log' -w start \
    -o \"-p $PORT -k '$DATA' -c listen_addresses=localhost -c fsync=off\"" >/dev/null
fi
DSN="host=localhost port=$PORT user=postgres"
if ! psql "$DSN dbname=postgres" -tAc "SELECT 1 FROM pg_database WHERE datname = 'handbook'" | grep -q 1; then
  psql "$DSN dbname=postgres" -qc "CREATE DATABASE handbook"
fi
echo "PostgreSQL is ready: $DSN dbname=handbook"
[ "$PORT" = "54329" ] || echo "Build with: HANDBOOK_PG_DSN=\"$DSN dbname=handbook\" python3 handbook/build.py"
