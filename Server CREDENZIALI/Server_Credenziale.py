import datetime
import os
import platform
import socket
import sqlite3
import ssl
import subprocess
from tkinter import messagebox
import msgpack
import pymerkle
from pymerkle import MerkleProof


def main():
    # Configura i file di certificato e chiave
    CERTIFICATE_FILE = '../CA/CA_root/CREDENZIALI_intermediate/certs/CREDENZIALI_Server.com.cert.pem'
    KEY_FILE = '../CA/CA_root/CREDENZIALI_intermediate/private/CREDENZIALI.com.key.pem'

    # Crea un contesto SSL con supporto per TLS 1.3
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(certfile=CERTIFICATE_FILE, keyfile=KEY_FILE)
    context.load_verify_locations("../CA/CA_root/CREDENZIALI_intermediate/certs/ca-chain.cert.pem")
    context.verify_mode = ssl.CERT_REQUIRED

    # Forza l'uso di TLS 1.3, se disponibile
    context.minimum_version = ssl.TLSVersion.TLSv1_3

    # Crea un socket di rete
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
    server_socket.bind(('0.0.0.0', 4435))  # Ascolta sulla porta 4435
    server_socket.listen(5)

    print("Server TLS in ascolto su port 4435...")

    while True:
        # Accetta una connessione in entrata
        client_socket, addr = server_socket.accept()
        print(f"Connessione accettata da {addr}")

        # Avvolgi il socket con SSL
        with context.wrap_socket(client_socket, server_side=True) as tls_client_socket:
            try:
                # Ricevi i dati dal client
                packed_data = tls_client_socket.recv(4096)  # Ricevi i dati in formato binario

                # Deserializzazione
                data_dict = msgpack.unpackb(packed_data, raw=False)

                tipo_credenziale = data_dict['tipo_credenziale']

                with open('../Server CREDENZIALI/dati.bin', 'rb') as file:
                    content = file.read()

                    # Trova il separatore di nuova linea (b'\n') che separa i due dati
                separator_index = content.find(b'\n')

                if separator_index == -1:
                    raise ValueError("Il file non contiene il separatore atteso.")

                # Estrai il numero del documento e la Merkle Root
                numero_documento = content[:separator_index].decode('utf-8')
                merkleRoot = content[separator_index + 1:]

                if os.path.exists('../Server CREDENZIALI/dati.bin'):
                    os.remove('../Server CREDENZIALI/dati.bin')

                if tipo_credenziale == '18+' or tipo_credenziale == 'Genere maschile' or tipo_credenziale == 'Genere femminile':

                    if tipo_credenziale == '18+':
                        data_nascita_str = data_dict['valore']
                        data_nascita = datetime.datetime.strptime(data_nascita_str, "%d/%m/%Y")
                        oggi = datetime.datetime.today()
                        eta = oggi.year - data_nascita.year - ((oggi.month, oggi.day) < (data_nascita.month, data_nascita.day))

                        # Verifica se l'età è sufficiente
                        if eta < 18:
                            messagebox.showerror("Errore", "Devi avere almeno 18 anni per continuare.")

                    base = data_dict['base']
                    proof_serial = data_dict['proof']
                    proof = MerkleProof.deserialize(proof_serial)

                    try:
                        pymerkle.verify_inclusion(base, merkleRoot, proof)
                    except Exception as e:
                        messagebox.showerror("Errore", "Hai inserito dati falsi!")

                else:

                    ISEE = data_dict['valore']
                    # Connessione al database SQLite (crea un nuovo database se non esiste)
                    conn = sqlite3.connect('../IPZS/ISEE.db')

                    # Creazione di un cursore per eseguire comandi SQL
                    cursor = conn.cursor()
                    cursor.execute('SELECT ISEE FROM documenti WHERE numero_documento = ?', (numero_documento,))
                    result = cursor.fetchone()
                    if result[0] != float(ISEE):
                        messagebox.showerror("Errore", "L'ISEE fornito non combacia con quello della banca dati INPS!")

                # Invia una risposta al client
                tls_client_socket.sendall(b'Hello from TLS server!')

                ########################################################################################################

                # Ricevi i dati dal client
                certificato = tls_client_socket.recv(4096)  # Ricevi i dati in formato binario

                with open("../Server CREDENZIALI/csr.pem", "wb") as file:
                    file.write(certificato)

                if platform.system() == 'Windows':
                    result = subprocess.run([r"C:\msys64\usr\bin\bash.exe", "../Server CREDENZIALI/Crea_Credenziale.sh", "../Server CREDENZIALI/csr.pem", numero_documento, tipo_credenziale], capture_output=True, text=True)
                else:
                    result = subprocess.run(["../Server CREDENZIALI/Crea_Credenziale.sh", "../Server CREDENZIALI/csr.pem", numero_documento, tipo_credenziale], capture_output=True, text=True)

                if os.path.exists('../Server CREDENZIALI/csr.pem'):
                    os.remove('../Server CREDENZIALI/csr.pem')

                if result.returncode != 0:
                    messagebox.showerror("Errore", "Si è verificato un errore durante la creazione della credenziale!")
                else:
                    tls_client_socket.sendall(b'Hello from TLS server!')

            except Exception as e:
                print(f"Errore del Server: {e}")
                if os.path.exists('../Server CREDENZIALI/dati.bin'):
                    os.remove('../Server CREDENZIALI/dati.bin')
                if os.path.exists('../Server CREDENZIALI/csr.pem'):
                    os.remove('../Server CREDENZIALI/csr.pem')


main()
