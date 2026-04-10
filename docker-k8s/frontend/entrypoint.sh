#!/bin/sh
set -e

# Fix permissions that nginx init script might fail on
chmod -R 777 /var/cache/nginx 2>/dev/null || true
chmod -R 777 /var/run 2>/dev/null || true

# Start nginx in foreground
nginx -g "daemon off;"

