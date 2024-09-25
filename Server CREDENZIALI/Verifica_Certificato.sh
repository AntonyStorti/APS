#!/bin/bash

# Verifico la validità del certificato ed estraggo la Merkle Root e il numero del documento

certificato=$1

numero_documento=$(openssl x509 -in "${certificato}" -noout -subject -nameopt RFC2253 | grep -o "CN=[^,]*" | sed 's/CN=//')


openssl verify -CAfile ../CA/CA_root/intermediate/CIE/"${numero_documento}"/chain.cert.pem "${certificato}"
merkle_root=$(openssl x509 -in "${certificato}" -noout -text | grep -A 1 "1.2.3" | grep ".@" | tr -d '.@')

echo "Numero del documento: ${numero_documento}"
echo "Merkle Root: ${merkle_root}"