#!/bin/bash

# Script utilizzato per generare le chiavi pubblica e privata dell'utente per l'ottenimento della credenziale

numero_documento=$1
tipo_credenziale=$2

cd ..
cd UTENTE/Certificati_Rilasciati/"${numero_documento}"
mkdir -p Credenziali
cd Credenziali
mkdir "${tipo_credenziale}"
cd "${tipo_credenziale}"

openssl ecparam -name prime256v1 -genkey -noout -out private_key.pem
openssl ec -in private_key.pem -pubout -out public_key.pem > /dev/null 2>&1
cd ..
cd ..
cd ..
cd ..
openssl req -config ../CA/CA_root/CREDENZIALI_intermediate/Credenziali.cnf -key ../UTENTE/Certificati_Rilasciati/"${numero_documento}"/Credenziali/"${tipo_credenziale}"/private_key.pem -new -sha256 -subj "/CN=${numero_documento}/C=IT/O=Richiesta Credenziale/OU=${tipo_credenziale}" -out ../UTENTE/Certificati_Rilasciati/"${numero_documento}"/Credenziali/"${tipo_credenziale}"/csr.pem -batch