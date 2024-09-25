import csv
import datetime
import os
import platform
import re
import socket
import sqlite3
import ssl
import subprocess
from pathlib import Path
import tkinter as tk
from tkinter import Tk, Canvas, Button, PhotoImage, messagebox, filedialog
import pygetwindow as gw
import msgpack
from pymerkle import SqliteTree as MerkleTree

OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path(r"./assets/frame2")

server_process = None


def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)


def credenziale_18():
    def verifica_data():
        data_nascita_str = entry.get()
        try:
            data_nascita = datetime.datetime.strptime(data_nascita_str, "%d/%m/%Y")
            connessione_TLS("18+", data_nascita_str)
        except ValueError:
            messagebox.showerror("Errore", "Formato data non valido. Usa il formato GG/MM/AAAA.")
        finally:
            window.destroy()

    window = tk.Tk()
    window.title("Inserisci la tua data di nascita")

    # Imposta la dimensione della finestra
    window.geometry("300x150")  # Larghezza x Altezza

    label = tk.Label(window, text="Data di nascita (GG/MM/AAAA):")
    label.pack(pady=10)

    entry = tk.Entry(window)
    entry.pack(pady=5)

    button = tk.Button(window, text="Invia", command=verifica_data)
    button.pack(pady=20)

    window.mainloop()


def credenziale_Genere():
    selected_genere = None  # Initialize with None to track selection

    def submit_genere():
        if selected_genere is None:
            messagebox.showerror("Errore", "Devi selezionare un genere.")
        else:
            if selected_genere == 'M':
                connessione_TLS("Genere maschile", selected_genere)
            elif selected_genere == 'F':
                connessione_TLS("Genere femminile", selected_genere)

        window.destroy()

    def set_genere(value):
        nonlocal selected_genere  # Ensure we're modifying the outer variable
        selected_genere = value

    window = tk.Tk()
    window.title("Inserimento Genere")

    # Imposta la dimensione della finestra
    window.geometry("300x150")  # Larghezza x Altezza

    tk.Label(window, text="Inserisci il genere (M o F):").pack(pady=10)

    tk.Radiobutton(window, text="Maschile (M)", value='M', variable=selected_genere, command=lambda: set_genere('M')).pack(anchor=tk.W)
    tk.Radiobutton(window, text="Femminile (F)", value='F', variable=selected_genere, command=lambda: set_genere('F')).pack(anchor=tk.W)

    tk.Button(window, text="Conferma", command=submit_genere).pack(pady=10)

    window.mainloop()


def credenziale_ISEE():
    # Funzione chiamata quando l'utente clicca su "Invia"
    def on_submit():
        isee = entry_ISEE.get()
        if not isee:
            messagebox.showwarning("Input mancante", "Per favore, inserisci l'ISEE.")
            return
        # Avvia la connessione TLS
        connessione_TLS(f"ISEE {isee}", isee)
        window.destroy()

    # Creazione della finestra principale
    window = tk.Tk()
    window.title("Inserisci ISEE")

    # Imposta la dimensione della finestra
    window.geometry("300x150")  # Larghezza x Altezza

    # Creazione e posizionamento degli elementi
    tk.Label(window, text="Inserisci il tuo ISEE:").pack(pady=10)
    entry_ISEE = tk.Entry(window)
    entry_ISEE.pack(pady=5)
    tk.Button(window, text="Invia", command=on_submit).pack(pady=10)

    # Avvio del loop dell'interfaccia grafica
    window.mainloop()


def recupera_numero_documento():
    with open('../Server CREDENZIALI/dati.bin', 'rb') as file:
        content = file.read()

    # Trova il separatore di nuova linea (b'\n') che separa i due dati
    separator_index = content.find(b'\n')

    if separator_index == -1:
        raise ValueError("Il file non contiene il separatore atteso.")

    # Estrai il numero del documento
    numero_documento = content[:separator_index].decode('utf-8')
    return numero_documento


def connessione_AGID(numero_documento, chiave_pubblica):
    nome_file = '../BlockChain/Credenziali.csv'

    # Controlla se il file esiste già
    file_esiste = os.path.isfile(nome_file)

    # Apri il file CSV in modalità append
    with open(nome_file, mode='a', newline='') as file:
        writer = csv.writer(file)

        # Scrivi l'intestazione se il file è nuovo
        if not file_esiste:
            writer.writerow(['Numero Documento', 'Chiave Pubblica'])

        # Scrivi le informazioni nel file
        writer.writerow([numero_documento, chiave_pubblica])


def connessione_TLS(tipo_credenziale, valore):
    numero_documento = recupera_numero_documento()

    server_address = ('localhost', 4435)  # Indirizzo e porta del server TLS
    global file_path
    try:
        # Crea un contesto SSL con supporto per TLS 1.3
        context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        context.load_cert_chain(certfile=f"../UTENTE/Certificati_Rilasciati/{numero_documento}/cert.pem", keyfile=f"../UTENTE/Certificati_Rilasciati/{numero_documento}/private_key.pem")
        context.load_verify_locations(f"../UTENTE/Certificati_Rilasciati/{numero_documento}/chain.cert.pem")
        context.minimum_version = ssl.TLSVersion.TLSv1_3
        context.verify_mode = ssl.CERT_REQUIRED

        if tipo_credenziale == '18+' or tipo_credenziale == 'Genere maschile' or tipo_credenziale == 'Genere femminile':

            file_path = filedialog.askopenfilename(
                title="Seleziona il file .db",
                filetypes=[("Database Files", "*.db")],
                initialdir="/"
            )

            if not file_path:
                messagebox.showwarning("Attenzione", "Nessun file selezionato. Operazione annullata.")
                return

        # Crea un socket di rete e stabilisci una connessione TLS
        with socket.create_connection(server_address) as sock:
            with context.wrap_socket(sock, server_hostname='localhost') as tls_sock:
                if tipo_credenziale == '18+' or tipo_credenziale == 'Genere maschile' or tipo_credenziale == 'Genere femminile':

                    tree = MerkleTree(file_path)

                    conn = sqlite3.connect(file_path)
                    cursor = conn.cursor()

                    try:
                        cursor.execute("SELECT id FROM leaf WHERE entry=?", (valore.encode(),))
                        rows = cursor.fetchone()

                        base = tree.get_leaf(rows[0])
                        proof = tree.prove_inclusion(rows[0])

                        proof_serial = proof.serialize()

                    except Exception as e:
                        messagebox.showerror("Errore", "Hai inserito dati falsi!")

                    # Creazione del dizionario
                    data = {
                        "tipo_credenziale": tipo_credenziale,
                        "valore": valore,
                        "base": base,
                        "proof": proof_serial  # Supponendo che `proof` sia in bytes e debba essere convertito in stringa
                    }

                    packed_data = msgpack.packb(data)

                    tls_sock.sendall(packed_data)

                else:
                    data = {
                        "tipo_credenziale": tipo_credenziale,
                        "valore": valore
                    }

                    packed_data = msgpack.packb(data)

                    tls_sock.sendall(packed_data)

                # Ricevi una risposta dal server
                response = tls_sock.recv(1024).decode('utf-8')

                if response == 'Hello from TLS server!':

                    if platform.system() == 'Windows':
                        result = subprocess.run([r"C:\msys64\usr\bin\bash.exe", "../UTENTE/Genera_chiavi_Windows.sh", numero_documento, tipo_credenziale], capture_output=True, text=True)
                    else:
                        result = subprocess.run(["../UTENTE/Genera_chiavi.sh", numero_documento, tipo_credenziale], capture_output=True, text=True)

                    if result.returncode == 0:

                        with open(f"../UTENTE/Certificati_Rilasciati/{numero_documento}/Credenziali/{tipo_credenziale}/csr.pem", "rb") as cert_file:
                            cert_data = cert_file.read()

                        tls_sock.sendall(cert_data)

                        # Ricevi una risposta dal server
                        response = tls_sock.recv(1024).decode('utf-8')

                        # Mostra un messaggio di successo se la risposta è quella attesa
                        if response == 'Hello from TLS server!':
                            messagebox.showinfo("Successo", f"La tua credenziale di tipo {tipo_credenziale} è stata ottenuta correttamente!")

                            pem_file = f"../UTENTE/Certificati_Rilasciati/{numero_documento}/Credenziali/{tipo_credenziale}/public_key.pem"
                            result = subprocess.run(['openssl', 'ec', '-in', pem_file, '-pubin', '-text', '-noout'], capture_output=True, text=True)
                            output = result.stdout

                            match = re.search(r'pub:\s*((?:\s*\w{2}:\s*){1,}\w{2})', output, re.MULTILINE)
                            if match:
                                chiave_pubblica = match.group(0).replace("pub:\n", "").replace(":", "").replace(" ", "").replace("\n", "")

                                connessione_AGID(numero_documento, chiave_pubblica)

                        else:
                            messagebox.showwarning("Attenzione", "Risposta inattesa dal server.")

                    else:
                        messagebox.showerror("Errore", result.stderr)

                else:
                    messagebox.showwarning("Attenzione", "Risposta inattesa dal server.")

    except (socket.error, ssl.SSLError) as e:
        # Gestisci le eccezioni di rete e SSL
        messagebox.showerror("Errore", f"Si è verificato un errore di connessione: {str(e)}")

    finally:
        stop_server()
        active_window = gw.getActiveWindow()
        active_window.close()


def avvia_server():
    global server_process
    server_process = subprocess.Popen(["python", "../Server CREDENZIALI/Server_Credenziale.py"])


def stop_server():
    if server_process:
        server_process.terminate()  # Invia un segnale di terminazione
        server_process.wait()       # Attende che il processo termini


def main():

    avvia_server()

    window = Tk()
    window.title("Scegli Credenziale")

    # Carica l'icona
    icon_image = PhotoImage(file="./icon.png")  # Assicurati che il file esista
    window.iconphoto(True, icon_image)  # Imposta l'icona della finestra

    window.geometry("1000x720")
    window.configure(bg = "#FFFFFF")


    canvas = Canvas(
        window,
        bg = "#FFFFFF",
        height = 720,
        width = 1000,
        bd = 0,
        highlightthickness = 0,
        relief = "ridge"
    )

    canvas.place(x = 0, y = 0)
    image_image_1 = PhotoImage(
        file=relative_to_assets("image_1.png"))
    image_1 = canvas.create_image(
        500.0,
        69.0,
        image=image_image_1
    )

    button_image_1 = PhotoImage(
        file=relative_to_assets("button_1.png"))
    button_1 = Button(
        image=button_image_1,
        borderwidth=0,
        highlightthickness=0,
        command=credenziale_18,
        relief="flat"
    )
    button_1.place(
        x=94.0,
        y=240.0,
        width=157.36196899414062,
        height=150.0
    )

    button_image_2 = PhotoImage(
        file=relative_to_assets("button_2.png"))
    button_2 = Button(
        image=button_image_2,
        borderwidth=0,
        highlightthickness=0,
        command=credenziale_Genere,
        relief="flat"
    )
    button_2.place(
        x=701.0,
        y=225.0,
        width=216.54135131835938,
        height=180.0
    )

    button_image_3 = PhotoImage(
        file=relative_to_assets("button_3.png"))
    button_3 = Button(
        image=button_image_3,
        borderwidth=0,
        highlightthickness=0,
        command=credenziale_ISEE,
        relief="flat"
    )
    button_3.place(
        x=299.0,
        y=405.0,
        width=402.0,
        height=267.0
    )

    canvas.create_rectangle(
        0.0,
        129.0,
        1000.0,
        145.0,
        fill="#000000",
        outline="")
    window.resizable(False, False)
    window.mainloop()


main()
