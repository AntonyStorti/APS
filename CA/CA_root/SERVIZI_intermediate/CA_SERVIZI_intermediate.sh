#!/bin/bash

# Script che genera SERVIZI_intermediate.

openssl ecparam -name prime256v1 -genkey -noout -out SERVIZI_intermediate/private/intermediate.key.pem
openssl ec -in SERVIZI_intermediate/private/intermediate.key.pem -pubout -out SERVIZI_intermediate/public_key.pem
openssl req -config SERVIZI_intermediate/CA_SERVIZI.cnf -new -sha256 -key SERVIZI_intermediate/private/intermediate.key.pem -out SERVIZI_intermediate/csr/intermediate.csr.pem
openssl ca -config CA_root.cnf -extensions v3_intermediate_ca -days 3650 -notext -md sha256 -in SERVIZI_intermediate/csr/intermediate.csr.pem -out SERVIZI_intermediate/certs/intermediate.cert.pem
openssl x509 -noout -text -in SERVIZI_intermediate/certs/intermediate.cert.pem
openssl verify -CAfile certs/ca.cert.pem SERVIZI_intermediate/certs/intermediate.cert.pem
cat SERVIZI_intermediate/certs/intermediate.cert.pem certs/ca.cert.pem > SERVIZI_intermediate/certs/ca-chain.cert.pem
# Per Windows:
# Get-Content -Path "SERVIZI_intermediate/certs/intermediate.cert.pem", "certs/ca.cert.pem" | Set-Content -Path "SERVIZI_intermediate/certs/ca-chain.cert.pem"
openssl x509 -in SERVIZI_intermediate/certs/ca-chain.cert.pem -text -noout
openssl verify -CAfile SERVIZI_intermediate/certs/ca-chain.cert.pem SERVIZI_intermediate/certs/intermediate.cert.pem