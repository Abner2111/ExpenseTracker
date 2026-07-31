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

# Anchored regex, not a shell glob: a glob like [0-9]*.[0-9]*.[0-9]*.[0-9]* looks
# IP-shaped but the bare `*` matches ANY characters (not just digits), so it was
# wrongly matching hostnames like 192.168.0.112.nip.io as an IP address too.
if printf '%s' "$SAN" | grep -Eq '^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$'; then
  ALT="IP:$SAN"
else
  ALT="DNS:$SAN"
fi

openssl req -x509 -newkey rsa:2048 -nodes -days 3650 \
  -keyout certs/key.pem -out certs/cert.pem \
  -subj "/CN=$SAN" \
  -addext "subjectAltName=$ALT"

echo "Wrote certs/cert.pem and certs/key.pem for $SAN"
