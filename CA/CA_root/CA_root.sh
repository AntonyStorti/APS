#!/bin/bash

# Script che genera la CA_root: "Ministero dell'Economia e delle Finanze"
openssl ecparam -name prime256v1 -genkey -noout -out ./private/ca.key.pem
openssl ec -in ./private/ca.key.pem -pubout -out public_key.pem
openssl req -config CA_root.cnf -key private/ca.key.pem -new -x509 -days 7300 -sha256 -extensions v3_ca -out certs/ca.cert.pem
openssl x509 -noout -text -in certs/ca.cert.pem

