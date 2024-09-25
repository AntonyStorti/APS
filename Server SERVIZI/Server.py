import os
import platform
import re
import socket
import ssl
import subprocess
from tkinter import messagebox
import ecdsa.ellipticcurve
from ecdsa.curves import NIST256p
from Verificatore import verifier
import msgpack
from BlockChain.AGID import blockchain


def main():
    # Configura i file di certificato e chiave
    CERTIFICATE_FILE = '../CA/CA_root/SERVIZI_intermediate/certs/SERVIZI_Server.com.cert.pem'
    KEY_FILE = '../CA/CA_root/SERVIZI_intermediate/private/SERVIZI.com.key.pem'

    # Crea un contesto SSL con supporto per TLS 1.3
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(certfile=CERTIFICATE_FILE, keyfile=KEY_FILE)
    context.load_verify_locations("../CA/CA_root/SERVIZI_intermediate/certs/ca-chain.cert.pem")

    # Forza l'uso di TLS 1.3, se disponibile
    context.minimum_version = ssl.TLSVersion.TLSv1_3

    # Crea un socket di rete
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
    server_socket.bind(('0.0.0.0', 4436))  # Ascolta sulla porta 4436
    server_socket.listen(5)

    print("Server TLS in ascolto su port 4436...")

    while True:
        # Accetta una connessione in entrata
        client_socket, addr = server_socket.accept()
        print(f"Connessione accettata da {addr}")

        # Avvolgi il socket con SSL
        with context.wrap_socket(client_socket, server_side=True) as tls_client_socket:
            try:

                tipo = tls_client_socket.recv(1024)

                tls_client_socket.sendall(b'Hello from TLS server!')

                if tipo == b'Poker':

                    certificato = tls_client_socket.recv(4096)

                    with open("../Server SERVIZI/cert.pem", "wb") as cert_file:
                        cert_file.write(certificato)

                    if platform.system() == 'Windows':
                        result = subprocess.run([r"C:\msys64\usr\bin\bash.exe", "../Server SERVIZI/Verifica.sh", "../Server SERVIZI/cert.pem"], capture_output=True, text=True)
                    else:
                        result = subprocess.run(["../Server SERVIZI/Verifica.sh", "../Server SERVIZI/cert.pem"], capture_output=True, text=True)

                    # Acquisisci l'output
                    output = result.stdout.strip().split("\n")

                    # Estrarre numero_documento e tipo_credenziale
                    if len(output) >= 2:
                        numero_documento = output[-2]
                        tipo_credenziale = output[-1]

                    if result.stderr == "" and tipo_credenziale == '18+':

                        messagebox.showinfo("Successo", "La tua credenziale è valida!")

                        public_key = subprocess.run(['openssl', 'x509', '-in', "../Server SERVIZI/cert.pem", '-pubkey', '-noout'], capture_output=True, text=True, check=True)

                        if public_key.stderr == "":

                            result = blockchain(numero_documento, public_key.stdout)

                            if result == True:

                                tls_client_socket.sendall(b'Hello from TLS server!')

                                data = tls_client_socket.recv(4096)
                                data_dict = msgpack.unpackb(data, raw=False)
                                u_bytes = data_dict.get('u')
                                u = ecdsa.ellipticcurve.PointJacobi.from_bytes(NIST256p.curve, u_bytes)
                                c_bytes = data_dict.get('c')
                                c = int.from_bytes(c_bytes, 'big')
                                z_bytes = data_dict.get('z')
                                z = int.from_bytes(z_bytes, 'big')
                                # Esegui il verifier
                                verifica = verifier(public_key.stdout, u, c, z)

                                if verifica == True:

                                    messagebox.showinfo("Successo", "Sei il vero possessore della credenziale!")

                                    tls_client_socket.sendall(b'Hello from TLS server!')

                            else:
                                messagebox.showerror("Errore", "Il certificato è contraffatto!")

                        else:
                            messagebox.showerror("Errore", "Problemi con l'estrazione della chiave pubblica!")

                    else:
                        messagebox.showerror("Errore", "La credenziale è falsa!")

                    if os.path.exists("../Server SERVIZI/cert.pem"):
                        os.remove("../Server SERVIZI/cert.pem")

                else:

                    certificato1 = tls_client_socket.recv(4096)

                    with open("../Server SERVIZI/cert.pem", "wb") as cert_file1:
                        cert_file1.write(certificato1)

                    if platform.system() == 'Windows':
                        result = subprocess.run([r"C:\msys64\usr\bin\bash.exe", "../Server SERVIZI/Verifica.sh", "../Server SERVIZI/cert.pem"], capture_output=True, text=True)
                    else:
                        result = subprocess.run(["../Server SERVIZI/Verifica.sh", "../Server SERVIZI/cert.pem"], capture_output=True, text=True)

                    # Acquisisci l'output
                    output = result.stdout.strip().split("\n")

                    # Estrarre numero_documento e tipo_credenziale
                    if len(output) >= 2:
                        numero_documento = output[-2]
                        tipo_credenziale = output[-1]

                    if result.stderr == "" and tipo_credenziale == '18+':

                        messagebox.showinfo("Successo", "La tua prima credenziale è valida!")

                        public_key = subprocess.run(['openssl', 'x509', '-in', "../Server SERVIZI/cert.pem", '-pubkey', '-noout'], capture_output=True, text=True, check=True)

                        if public_key.stderr == "":

                            result = blockchain(numero_documento, public_key.stdout)

                            if result == True:

                                tls_client_socket.sendall(b'Hello from TLS server!')

                                data = tls_client_socket.recv(4096)
                                data_dict = msgpack.unpackb(data, raw=False)
                                u_bytes = data_dict.get('u')
                                u = ecdsa.ellipticcurve.PointJacobi.from_bytes(NIST256p.curve, u_bytes)
                                c_bytes = data_dict.get('c')
                                c = int.from_bytes(c_bytes, 'big')
                                z_bytes = data_dict.get('z')
                                z = int.from_bytes(z_bytes, 'big')
                                # Esegui il verifier
                                verifica = verifier(public_key.stdout, u, c, z)

                                if verifica == True:

                                    messagebox.showinfo("Successo", "Sei il vero possessore della credenziale!")

                                    tls_client_socket.sendall(b'Hello from TLS server!')

                                    if os.path.exists("../Server SERVIZI/cert.pem"):
                                        os.remove("../Server SERVIZI/cert.pem")

                                    certificato2 = tls_client_socket.recv(4096)

                                    with open("../Server SERVIZI/cert.pem", "wb") as cert_file2:
                                        cert_file2.write(certificato2)

                                    if platform.system() == 'Windows':
                                        result = subprocess.run([r"C:\msys64\usr\bin\bash.exe", "../Server SERVIZI/Verifica.sh", "../Server SERVIZI/cert.pem"], capture_output=True, text=True)
                                    else:
                                        result = subprocess.run(["../Server SERVIZI/Verifica.sh", "../Server SERVIZI/cert.pem"], capture_output=True, text=True)

                                    # Acquisisci l'output
                                    output = result.stdout.strip().split("\n")

                                    # Estrarre numero_documento e tipo_credenziale
                                    if len(output) >= 2:
                                        numero_documento2 = output[-2]
                                        tipo_credenziale2 = output[-1]

                                    valore_ISEE = int(re.search(r'\d+', tipo_credenziale2).group())

                                    if result.stderr == "" and numero_documento == numero_documento2 and valore_ISEE <= 7000:

                                        messagebox.showinfo("Successo", "La tua seconda credenziale è valida!")

                                        public_key = subprocess.run(['openssl', 'x509', '-in', "../Server SERVIZI/cert.pem", '-pubkey', '-noout'], capture_output=True, text=True, check=True)

                                        if public_key.stderr == "":

                                            result = blockchain(numero_documento, public_key.stdout)

                                            if result == True:

                                                tls_client_socket.sendall(b'Hello from TLS server!')

                                                data = tls_client_socket.recv(4096)
                                                data_dict = msgpack.unpackb(data, raw=False)
                                                u_bytes = data_dict.get('u')
                                                u = ecdsa.ellipticcurve.PointJacobi.from_bytes(NIST256p.curve, u_bytes)
                                                c_bytes = data_dict.get('c')
                                                c = int.from_bytes(c_bytes, 'big')
                                                z_bytes = data_dict.get('z')
                                                z = int.from_bytes(z_bytes, 'big')
                                                # Esegui il verifier
                                                verifica = verifier(public_key.stdout, u, c, z)

                                                if verifica == True:

                                                    messagebox.showinfo("Successo", "Sei il vero possessore della credenziale!")

                                                    tls_client_socket.sendall(b'Hello from TLS server!')

                                            else:
                                                messagebox.showerror("Errore", "Il certificato è contraffatto!")

                                        else:
                                            messagebox.showerror("Errore", "Problemi con l'estrazione della chiave pubblica!")

                                    elif numero_documento != numero_documento2:
                                        messagebox.showerror("Errore", "Le due credenziali non appartengono alla stessa persona!")

                                    elif valore_ISEE > 7000:
                                        messagebox.showerror("Errore", "Il valore dell'ISEE non rispetta il requisito richiesto per l'accesso!")

                                    else:
                                        messagebox.showerror("Errore", "La credenziale è falsa!")

                                    if os.path.exists("../Server SERVIZI/cert.pem"):
                                        os.remove("../Server SERVIZI/cert.pem")

                                else:
                                    messagebox.showerror("Errore", "Non sei il vero possessore della credenziale!")

                            else:
                                messagebox.showerror("Errore", "Il certificato è contraffatto!")

                        else:
                            messagebox.showerror("Errore", "Problemi con l'estrazione della chiave pubblica!")

                    else:
                        messagebox.showerror("Errore", "La credenziale è falsa!")

                    if os.path.exists("../Server SERVIZI/cert.pem"):
                        os.remove("../Server SERVIZI/cert.pem")

            except Exception as e:
                print(f"Errore del Server: {e}")
                if os.path.exists("../Server SERVIZI/cert.pem"):
                    os.remove("../Server SERVIZI/cert.pem")


main()
