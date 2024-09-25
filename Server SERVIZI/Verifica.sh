#!/bin/bash

# Verifico la validità del certificato ed estraggo il numero del documento

certificato=$1

numero_documento=$(openssl x509 -in "${certificato}" -noout -subject -nameopt RFC2253 | grep -o "CN=[^,]*" | sed 's/CN=//')
tipo_credenziale=$(openssl x509 -in "${certificato}" -noout -subject -nameopt RFC2253 | grep -o "OU=[^,]*" | sed 's/OU=//' | sed 's/\\//g')
openssl verify -CAfile ../CA/CA_root/CREDENZIALI_intermediate/CREDENZIALI/"${numero_documento}"/"${tipo_credenziale}"/chain.cert.pem "${certificato}"

echo "${numero_documento}"
echo "${tipo_credenziale}"