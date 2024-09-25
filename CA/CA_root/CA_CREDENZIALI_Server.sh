#!/bin/bash

# Script che genera il Server di CREDENZIALI_intermediate.

openssl ecparam -name prime256v1 -genkey -noout -out CREDENZIALI_intermediate/private/CREDENZIALI.com.key.pem
openssl ec -in CREDENZIALI_intermediate/private/CREDENZIALI.com.key.pem -pubout -out CREDENZIALI_intermediate/CREDENZIALI_public_key.pem
openssl req -config CREDENZIALI_intermediate/CA_RILASCIO_CREDENZIALI.cnf -key CREDENZIALI_intermediate/private/CREDENZIALI.com.key.pem -new -sha256 -out CREDENZIALI_intermediate/csr/CREDENZIALI.com.csr.pem -addext "subjectAltName = DNS:localhost"
openssl ca -config CREDENZIALI_intermediate/CA_RILASCIO_CREDENZIALI.cnf -extensions server_cert -days 375 -notext -md sha256 -in CREDENZIALI_intermediate/csr/CREDENZIALI.com.csr.pem -out CREDENZIALI_intermediate/certs/CREDENZIALI_Server.com.cert.pem
openssl x509 -noout -text -in CREDENZIALI_intermediate/certs/CREDENZIALI_Server.com.cert.pem
openssl verify -CAfile CREDENZIALI_intermediate/certs/ca-chain.cert.pem CREDENZIALI_intermediate/certs/CREDENZIALI_Server.com.cert.pem
