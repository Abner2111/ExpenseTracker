#!/bin/sh
# Generates a self-signed TLS cert for the web UI. Needed because Google's OAuth
# server refuses to redirect back to a plain-HTTP address unless it's localhost -
# a LAN IP like 192.168.0.112 needs https://, even if the cert isn't CA-signed
# (the browser just needs to be told to trust it once; Google never validates it
# itself since the redirect is a client-side browser hop, not a server fetch).
#
# Usage: ./deploy/gen-cert.sh <ip-or-hostname>
# Run from the repo root. Writes certs/cert.pem and certs/key.pem.

set -e

SAN="${1:?Usage: gen-cert.sh <ip-or-hostname>}"
mkdir -p certs

case "$SAN" in
  [0-9]*.[0-9]*.[0-9]*.[0-9]*) ALT="IP:$SAN" ;;
  *) ALT="DNS:$SAN" ;;
esac

openssl req -x509 -newkey rsa:2048 -nodes -days 3650 \
  -keyout certs/key.pem -out certs/cert.pem \
  -subj "/CN=$SAN" \
  -addext "subjectAltName=$ALT"

echo "Wrote certs/cert.pem and certs/key.pem for $SAN"
