#!/bin/bash

# Script che emula il "Rilascio della CIE" da parte di IPZS

root_merkle=$1
numero_documento=$2

cd ..
cd CA/CA_root
mkdir intermediate/CIE/"${numero_documento}"
openssl ecparam -name prime256v1 -genkey -noout -out intermediate/CIE/"${numero_documento}"/private_key.pem
openssl ec -in intermediate/CIE/"${numero_documento}"/private_key.pem -pubout -out intermediate/CIE/"${numero_documento}"/public_key.pem
openssl req -config intermediate/Certificato_CIE.cnf -key intermediate/CIE/"${numero_documento}"/private_key.pem -new -sha256 -subj "/CN=${numero_documento}/C=IT/ST=Lazio/L=Rome/O=Ministero dell'Interno/OU=Dipartimento Anagrafe Civile/emailAddress=admin@interno.anagrafe.it" -addext "subjectAltName=DNS:localhost" -addext "1.2.3=ASN1:UTF8String:${root_merkle}" -out intermediate/CIE/"${numero_documento}"/csr.pem -batch
openssl ca -config intermediate/Certificato_CIE.cnf -extensions usr_cert -days 375 -notext -md sha256 -in intermediate/CIE/"${numero_documento}"/csr.pem -out intermediate/CIE/"${numero_documento}"/cert.pem -batch
openssl x509 -noout -text -in intermediate/CIE/"${numero_documento}"/cert.pem
cat intermediate/CIE/"${numero_documento}"/cert.pem intermediate/certs/ca-chain.cert.pem > intermediate/CIE/"${numero_documento}"/chain.cert.pem
openssl verify -CAfile intermediate/CIE/"${numero_documento}"/chain.cert.pem intermediate/CIE/"${numero_documento}"/cert.pem
cd ..
cd ..
cp -r CA/CA_root/intermediate/CIE/"${numero_documento}" UTENTE/Certificati_Rilasciati/"${numero_documento}"/
rm UTENTE/Certificati_Rilasciati/"${numero_documento}"/csr.pem