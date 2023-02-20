#!/bin/sh

/usr/src/app/tailscaled --state=/var/lib/tailscale/tailscaled.state --socket=/var/run/tailscale/tailscaled.sock &
sleep 2
/usr/src/app/tailscale up --authkey="${TAILSCALE_AUTHKEY}" --hostname=exporter-fly-app --accept-routes

python /usr/src/app/main.py
