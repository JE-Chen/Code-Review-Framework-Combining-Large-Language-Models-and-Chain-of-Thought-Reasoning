#!/bin/sh
# Substitute the token from env into nginx.conf at container start.
# Refuses to start if the variable is missing — fail-fast avoids silently
# accepting any bearer token.
set -eu

if [ -z "${REVIEWMIND_BACKEND_TOKEN:-}" ]; then
  echo "FATAL: REVIEWMIND_BACKEND_TOKEN is not set." >&2
  echo "Add it to your .env file before running docker compose up." >&2
  exit 1
fi

sed -i "s|__REVIEWMIND_BACKEND_TOKEN__|${REVIEWMIND_BACKEND_TOKEN}|g" \
    /etc/nginx/nginx.conf

exec nginx -g 'daemon off;'
