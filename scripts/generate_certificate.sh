#!/bin/bash
# Use this script to generate a self-signed certificate for jupyterhub.
# Normally needed only when we deploy an experimental installation for the
# first time.
openssl genrsa -des3 -out test.key 1024
openssl req -new -key test.key -out test.csr
cp test.key test.key.org
openssl rsa -in test.key.org -out test.key
openssl x509 -req -days 365 -in test.csr -signkey test.key -out test.crt

