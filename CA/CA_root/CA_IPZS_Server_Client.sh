#!/bin/bash

# Script che genera certificati per Server e Client IPZS (Servizio Anagrafe)

openssl ecparam -name prime256v1 -genkey -noout -out intermediate/private/IPZS.com.key.pem
openssl ec -in intermediate/private/IPZS.com.key.pem -pubout -out intermediate/IPZS_public_key.pem
openssl req -config intermediate/CA_IPZS_CIE.cnf -key intermediate/private/IPZS.com.key.pem -new -sha256 -out intermediate/csr/IPZS.com.csr.pem -addext "subjectAltName = DNS:localhost"
openssl ca -config intermediate/CA_IPZS_CIE.cnf -extensions server_cert -days 375 -notext -md sha256 -in intermediate/csr/IPZS.com.csr.pem -out intermediate/certs/IPZS_Server.com.cert.pem
openssl x509 -noout -text -in intermediate/certs/IPZS_Server.com.cert.pem
openssl verify -CAfile intermediate/certs/ca-chain.cert.pem intermediate/certs/IPZS_Server.com.cert.pem
openssl req -config intermediate/CA_IPZS_CIE.cnf -key intermediate/private/IPZS.com.key.pem -new -sha256 -out intermediate/csr/IPZS_Client.com.csr.pem -addext "subjectAltName = DNS:localhost"
openssl ca -config intermediate/CA_IPZS_CIE.cnf -extensions usr_cert -days 375 -notext -md sha256 -in intermediate/csr/IPZS_Client.com.csr.pem -out intermediate/certs/IPZS_Client.com.cert.pem
openssl x509 -noout -text -in intermediate/certs/IPZS_Client.com.cert.pem
openssl verify -CAfile intermediate/certs/ca-chain.cert.pem intermediate/certs/IPZS_Client.com.cert.pem