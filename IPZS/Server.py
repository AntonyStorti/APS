import json
import platform
import subprocess
from datetime import datetime, timedelta
import random
import string
import socket
import ssl
from pymerkle import SqliteTree as MerkleTree


def generate_random_code(length=8):
    """Genera un codice alfanumerico casuale di lunghezza specificata."""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))


def genera_CIE(data):
    str_data = data.decode("utf-8")
    data_dict = json.loads(str_data)

    # Data di emissione: la data attuale
    data_emissione = datetime.now().strftime('%d/%m/%Y')

    # Data di scadenza: la data attuale + 10 anni
    data_scadenza = (datetime.now() + timedelta(days=10 * 365)).strftime('%d/%m/%Y')

    # Numero documento: codice alfanumerico casuale
    numero_documento = generate_random_code()

    # Aggiungi i nuovi elementi al dizionario
    data_dict["Data emissione"] = data_emissione
    data_dict["Data scadenza"] = data_scadenza
    data_dict["Numero documento"] = numero_documento

    # Prepara i dati per il Merkle Tree (solo valori)
    values = list(data_dict.values())

    codice_fiscale = data_dict.get("Codice Fiscale")

    db_name = f"../UTENTE/Database/{codice_fiscale}.db"

    # Crea un Merkle Tree usando il nome del database personalizzato
    tree = MerkleTree(db_name)

    # Aggiungi le foglie al Merkle Tree
    for value in values:
        # Converti il valore in bytes per l'aggiunta al Merkle Tree
        tree.append_entry(value.encode())

    root_merkle = tree.get_state()

    root_merkle_hex = root_merkle.hex()

    if platform.system() == 'Windows':
        subprocess.run([r"C:\msys64\usr\bin\bash.exe", "../IPZS/OnlyWindows.sh", root_merkle_hex, numero_documento])
    else:
        subprocess.run(["../IPZS/Genera_Certificato.sh", root_merkle_hex, numero_documento])


def main():
    # Configura i file di certificato e chiave
    CERTIFICATE_FILE = '../CA/CA_root/intermediate/certs/IPZS_Server.com.cert.pem'
    KEY_FILE = '../CA/CA_root/intermediate/private/IPZS.com.key.pem'

    # Crea un contesto SSL con supporto per TLS 1.3
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(certfile=CERTIFICATE_FILE, keyfile=KEY_FILE)
    context.load_verify_locations("../CA/CA_root/intermediate/certs/ca-chain.cert.pem")

    # Forza l'uso di TLS 1.3, se disponibile
    context.minimum_version = ssl.TLSVersion.TLSv1_3

    context.verify_mode = ssl.CERT_REQUIRED

    # Crea un socket di rete
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
    server_socket.bind(('0.0.0.0', 4433))  # Ascolta sulla porta 4433
    server_socket.listen(5)

    print("Server TLS in ascolto su port 4433...")

    while True:
        # Accetta una connessione in entrata
        client_socket, addr = server_socket.accept()
        print(f"Connessione accettata da {addr}")

        # Avvolgi il socket con SSL
        with context.wrap_socket(client_socket, server_side=True) as tls_client_socket:
            try:
                # Ricevi dati dal client
                data = tls_client_socket.recv(1024)
                genera_CIE(data)

                # Invia una risposta al client
                tls_client_socket.sendall(b'Hello from TLS server!')

            except Exception as e:
                print(f"Errore del Server: {e}")


main()
