#!/bin/bash

# Script che firma la richiesta della credenziale effettuata dall'utente.

csr=$1
numero_documento=$2
tipo_credenziale=$3

mkdir -p ../CA/CA_root/CREDENZIALI_intermediate/CREDENZIALI/"${numero_documento}"
mkdir ../CA/CA_root/CREDENZIALI_intermediate/CREDENZIALI/"${numero_documento}"/"${tipo_credenziale}"

openssl ca -config ../CA/CA_root/CREDENZIALI_intermediate/Credenziali.cnf -extensions usr_cert -days 30 -notext -md sha256 -in "${csr}" -out ../CA/CA_root/CREDENZIALI_intermediate/CREDENZIALI/"${numero_documento}"/"${tipo_credenziale}"/"${tipo_credenziale}".pem -batch > /dev/null 2>&1
openssl x509 -noout -text -in ../CA/CA_root/CREDENZIALI_intermediate/CREDENZIALI/"${numero_documento}"/"${tipo_credenziale}"/"${tipo_credenziale}".pem > /dev/null 2>&1
cat ../CA/CA_root/CREDENZIALI_intermediate/CREDENZIALI/"${numero_documento}"/"${tipo_credenziale}"/"${tipo_credenziale}".pem ../CA/CA_root/CREDENZIALI_intermediate/certs/ca-chain.cert.pem > ../CA/CA_root/CREDENZIALI_intermediate/CREDENZIALI/"${numero_documento}"/"${tipo_credenziale}"/chain.cert.pem
openssl verify -CAfile ../CA/CA_root/CREDENZIALI_intermediate/CREDENZIALI/"${numero_documento}"/"${tipo_credenziale}"/chain.cert.pem ../CA/CA_root/CREDENZIALI_intermediate/CREDENZIALI/"${numero_documento}"/"${tipo_credenziale}"/"${tipo_credenziale}".pem > /dev/null 2>&1
cp -r ../CA/CA_root/CREDENZIALI_intermediate/CREDENZIALI/"${numero_documento}"/"${tipo_credenziale}"/. ../UTENTE/Certificati_Rilasciati/"${numero_documento}"/Credenziali/"${tipo_credenziale}"