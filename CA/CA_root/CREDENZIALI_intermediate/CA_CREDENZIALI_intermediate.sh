#!/bin/bash

# Script per la generazione di CREDENZIALI_intermediate.

openssl ecparam -name prime256v1 -genkey -noout -out CREDENZIALI_intermediate/private/intermediate.key.pem
openssl ec -in CREDENZIALI_intermediate/private/intermediate.key.pem -pubout -out CREDENZIALI_intermediate/public_key.pem
openssl req -config CREDENZIALI_intermediate/CA_CREDENZIALI.cnf -new -sha256 -key CREDENZIALI_intermediate/private/intermediate.key.pem -out CREDENZIALI_intermediate/csr/intermediate.csr.pem
openssl ca -config CA_root.cnf -extensions v3_intermediate_ca -days 3650 -notext -md sha256 -in CREDENZIALI_intermediate/csr/intermediate.csr.pem -out CREDENZIALI_intermediate/certs/intermediate.cert.pem
openssl x509 -noout -text -in CREDENZIALI_intermediate/certs/intermediate.cert.pem
openssl verify -CAfile certs/ca.cert.pem CREDENZIALI_intermediate/certs/intermediate.cert.pem
cat CREDENZIALI_intermediate/certs/intermediate.cert.pem certs/ca.cert.pem > CREDENZIALI_intermediate/certs/ca-chain.cert.pem
openssl x509 -in CREDENZIALI_intermediate/certs/ca-chain.cert.pem -text -noout
openssl verify -CAfile CREDENZIALI_intermediate/certs/ca-chain.cert.pem CREDENZIALI_intermediate/certs/intermediate.cert.pem