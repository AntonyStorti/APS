#!/bin/bash

# Script che crea la CA intermedia: IPZS
openssl ecparam -name prime256v1 -genkey -noout -out intermediate/private/intermediate.key.pem
openssl ec -in intermediate/private/intermediate.key.pem -pubout -out intermediate/public_key.pem
openssl req -config intermediate/CA_IPZS.cnf -new -sha256 -key intermediate/private/intermediate.key.pem -out intermediate/csr/intermediate.csr.pem
openssl ca -config CA_root.cnf -extensions v3_intermediate_ca -days 3650 -notext -md sha256 -in intermediate/csr/intermediate.csr.pem -out intermediate/certs/intermediate.cert.pem
openssl x509 -noout -text -in intermediate/certs/intermediate.cert.pem
openssl verify -CAfile certs/ca.cert.pem intermediate/certs/intermediate.cert.pem
cat intermediate/certs/intermediate.cert.pem certs/ca.cert.pem > intermediate/certs/ca-chain.cert.pem
openssl x509 -in intermediate/certs/ca-chain.cert.pem -text -noout
openssl verify -CAfile intermediate/certs/ca-chain.cert.pem intermediate/certs/intermediate.cert.pem