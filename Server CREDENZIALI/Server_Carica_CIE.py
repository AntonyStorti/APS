import os
import platform
import socket
import ssl
import subprocess


def main():
    # Configura i file di certificato e chiave
    CERTIFICATE_FILE = '../CA/CA_root/CREDENZIALI_intermediate/certs/CREDENZIALI_Server.com.cert.pem'
    KEY_FILE = '../CA/CA_root/CREDENZIALI_intermediate/private/CREDENZIALI.com.key.pem'

    # Crea un contesto SSL con supporto per TLS 1.3
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(certfile=CERTIFICATE_FILE, keyfile=KEY_FILE)
    context.verify_mode = ssl.CERT_NONE

    # Forza l'uso di TLS 1.3, se disponibile
    context.minimum_version = ssl.TLSVersion.TLSv1_3

    # Crea un socket di rete
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
    server_socket.bind(('0.0.0.0', 4434))  # Ascolta sulla porta 4434
    server_socket.listen(5)

    print("Server TLS in ascolto su port 4434...")

    while True:
        # Accetta una connessione in entrata
        client_socket, addr = server_socket.accept()
        print(f"Connessione accettata da {addr}")

        # Avvolgi il socket con SSL
        with context.wrap_socket(client_socket, server_side=True) as tls_client_socket:
            try:
                certificato = tls_client_socket.recv(4096)
                with open("../Server CREDENZIALI/cert.pem", "wb") as cert_file:
                    cert_file.write(certificato)

                if platform.system() == 'Windows':
                    result = subprocess.run([r"C:\msys64\usr\bin\bash.exe", "../Server CREDENZIALI/Verifica_Certificato.sh", "../Server CREDENZIALI/cert.pem"], capture_output=True, text=True)
                else:
                    result = subprocess.run(["../Server CREDENZIALI/Verifica_Certificato.sh", "../Server CREDENZIALI/cert.pem"], capture_output=True, text=True)

                lines = result.stdout.splitlines()
                numero_documento = None
                merkleRoot = None

                for line in lines:
                    if line.startswith("Numero del documento:"):
                        numero_documento = line.split(": ")[1]
                        numero_documento = numero_documento.strip()
                    elif line.startswith("Merkle Root:"):
                        merkleRoot = line.split(": ")[1]
                        merkleRoot = merkleRoot.strip()
                        merkleRoot = bytes.fromhex(merkleRoot)

                with open('../Server CREDENZIALI/dati.bin', 'wb') as file:
                    file.write(numero_documento.encode('utf-8'))
                    file.write(b'\n')  # Aggiungi una nuova linea come separatore
                    # Scrivi la Merkle Root come binario
                    file.write(merkleRoot)

                if result.stderr == "":
                    tls_client_socket.sendall(b'Hello from TLS server!')
                else:
                    # Invia una risposta al client
                    tls_client_socket.send(result.stderr.encode('utf-8'))

            except Exception as e:
                print(f"Errore del Server: {e}")

            finally:
                if os.path.exists("../Server CREDENZIALI/cert.pem"):
                    os.remove("../Server CREDENZIALI/cert.pem")


main()
