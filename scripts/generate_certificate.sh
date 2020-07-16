#!/bin/bash
# Use this script to generate a self-signed certificate for jupyterhub.
# Normally needed only when we deploy an experimental installation for the
# first time.

type=$1
simphony_remote=$2

if [ $type = 'test' ]
then

  directory=${simphony_remote}/jupyterhub

  if test -e ${directory}/test.crt
  then
      echo "Certificate already present, skipping. Delete the current certificate to recreate."
      exit 0
  fi

  echo "Generating self-signed certificates in $directory"

  openssl genrsa -out ${directory}/test.key 1024
  openssl req -new -key ${directory}/test.key -out ${directory}/test.csr -batch
  cp ${directory}/test.key ${directory}/test.key.org
  openssl rsa -in ${directory}/test.key.org -out ${directory}/test.key
  openssl x509 -req -days 365 -in ${directory}/test.csr -signkey ${directory}/test.key -out ${directory}/test.crt

elif [ $type = 'nginx' ]
then

  directory=${simphony_remote}/nginx/certs

  if [ ! -d $directory ]; then \
		mkdir $directory
	fi

  if test -e ${directory}/nginx-selfsigned.crt
  then
      echo "Certificate already present, skipping. Delete the current certificate to recreate."
      exit 0
  fi

  echo "Generating Nginx certificates."

  openssl req -x509 -nodes -days 365 \
    -newkey rsa:2048 \
    -keyout ${directory}/nginx-selfsigned.key \
    -out ${directory}/nginx-selfsigned.crt

  openssl dhparam -out ${directory}/dhparam.pem 2048 # Use 4096 for production deployment

fi
