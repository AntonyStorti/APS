#!/bin/bash

# Script che genera il Server di SERVIZI_intermediate.

openssl ecparam -name prime256v1 -genkey -noout -out SERVIZI_intermediate/private/SERVIZI.com.key.pem
openssl ec -in SERVIZI_intermediate/private/SERVIZI.com.key.pem -pubout -out SERVIZI_intermediate/SERVIZI_public_key.pem
openssl req -config SERVIZI_intermediate/CA_UTILIZZO_CREDENZIALI.cnf -key SERVIZI_intermediate/private/SERVIZI.com.key.pem -new -sha256 -out SERVIZI_intermediate/csr/SERVIZI.com.csr.pem -addext "subjectAltName = DNS:localhost"
openssl ca -config SERVIZI_intermediate/CA_UTILIZZO_CREDENZIALI.cnf -extensions server_cert -days 375 -notext -md sha256 -in SERVIZI_intermediate/csr/SERVIZI.com.csr.pem -out SERVIZI_intermediate/certs/SERVIZI_Server.com.cert.pem
openssl x509 -noout -text -in SERVIZI_intermediate/certs/SERVIZI_Server.com.cert.pem
openssl verify -CAfile SERVIZI_intermediate/certs/ca-chain.cert.pem SERVIZI_intermediate/certs/SERVIZI_Server.com.cert.pem
