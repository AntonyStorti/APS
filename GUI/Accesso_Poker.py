import socket
import ssl
import subprocess
from pathlib import Path
from tkinter import Tk, Canvas, Button, PhotoImage, filedialog, messagebox
import msgpack
import pygetwindow as gw
from UTENTE.Provatore import prover

OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path(r"./assets/frame5")

server_process = None


def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)


def choose_file():
    global file_path
    # Apre una finestra di dialogo per la selezione di un file
    file_path = filedialog.askopenfilename(
        title="Seleziona un file",
        filetypes=[("File PEM", "*.pem")]
    )
    if file_path:
        # Mostra il percorso del file selezionato (puoi gestirlo come preferisci)
        messagebox.showinfo("File Selezionato", f"File selezionato: {file_path}")


def connessione_TLS():

    server_address = ('localhost', 4436)  # Indirizzo e porta del server TLS

    try:
        # Crea un contesto SSL con supporto per TLS 1.3
        context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        context.load_verify_locations("../CA/CA_root/SERVIZI_intermediate/certs/ca-chain.cert.pem")
        context.minimum_version = ssl.TLSVersion.TLSv1_3
        context.verify_mode = ssl.CERT_REQUIRED

        # Crea un socket di rete e stabilisci una connessione TLS
        with socket.create_connection(server_address) as sock:
            with context.wrap_socket(sock, server_hostname='localhost') as tls_sock:

                tls_sock.sendall(b'Poker')

                # Ricevi una risposta dal server
                response = tls_sock.recv(1024).decode('utf-8')

                # Mostra un messaggio di successo se la risposta è quella attesa
                if response == 'Hello from TLS server!':

                    certificato = file_path
                    with open(certificato, "rb") as cert_file:
                        cert_data = cert_file.read()

                    # Invia i dati al server
                    tls_sock.sendall(cert_data)

                    # Ricevi una risposta dal server
                    response = tls_sock.recv(1024).decode('utf-8')

                    # Mostra un messaggio di successo se la risposta è quella attesa
                    if response == 'Hello from TLS server!':

                        messagebox.showinfo("Schnorr ZKP", "Ti verrà chiesto di caricare la tua chiave privata, non verrà assolutamente inviata ad alcun server, servirà per eseguire il protocollo ZKP in locale!")

                        private_key = filedialog.askopenfilename(
                            title="Seleziona un file",
                            filetypes=[("File PEM", "*.pem")]
                        )

                        # Carica la chiave privata e pubblica da file PEM
                        with open(private_key, "r") as f:
                            private_key_pem = f.read()

                        # Esegui il prover
                        u, c, z = prover(private_key_pem)
                        data_dict = {
                            'u': u.to_bytes(),
                            'c': c.to_bytes(32, 'big'),
                            'z': z.to_bytes(32, 'big')
                        }
                        data = msgpack.packb(data_dict, use_bin_type=True)
                        tls_sock.sendall(data)

                        # Ricevi una risposta dal server
                        response = tls_sock.recv(1024).decode('utf-8')

                        if response == 'Hello from TLS server!':
                            messagebox.showinfo("Successo", "Puoi accedere al servizio!")
                        else:
                            messagebox.showerror("Errore", "Non sei il vero possessore della credenziale!")

                    else:
                        messagebox.showwarning("Attenzione", "Risposta inattesa dal server.")

                else:
                    messagebox.showerror("Errore", "Risposta inattesa dal server.")

    except (socket.error, ssl.SSLError) as e:
        # Gestisci le eccezioni di rete e SSL
        messagebox.showerror("Errore", f"Si è verificato un errore di connessione: {str(e)}")

    finally:
        stop_server()
        active_window = gw.getActiveWindow()
        active_window.close()


def avvia_server():
    global server_process
    server_process = subprocess.Popen(["python", "../Server SERVIZI/Server.py"])


def stop_server():
    if server_process:
        server_process.terminate()  # Invia un segnale di terminazione
        server_process.wait()       # Attende che il processo termini


def main():
    avvia_server()
    window = Tk()
    window.title("Accesso Poker")

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
    canvas.create_text(
        18.0,
        13.0,
        anchor="nw",
        text="ACCEDI",
        fill="#000000",
        font=("Inter Black", 40 * -1)
    )

    canvas.create_rectangle(
        0.0,
        82.0,
        1000.0,
        98.0,
        fill="#FF0000",
        outline="")

    canvas.create_text(
        94.0,
        297.0,
        anchor="nw",
        text="Carica la tua credenziale:",
        fill="#000000",
        font=("Inter ExtraLight", 32 * -1)
    )

    canvas.create_text(
        207.0,
        116.0,
        anchor="nw",
        text="Per giocare a Poker devi essere maggiorenne!!! ",
        fill="#000000",
        font=("Inter Black", 24 * -1)
    )

    button_image_1 = PhotoImage(
        file=relative_to_assets("button_1.png"))
    button_1 = Button(
        image=button_image_1,
        borderwidth=0,
        highlightthickness=0,
        command=choose_file,
        relief="flat"
    )
    button_1.place(
        x=587.0,
        y=289.0,
        width=246.0,
        height=64.0
    )

    button_image_2 = PhotoImage(
        file=relative_to_assets("button_2.png"))
    button_2 = Button(
        image=button_image_2,
        borderwidth=0,
        highlightthickness=0,
        command=connessione_TLS,
        relief="flat"
    )
    button_2.place(
        x=350.0,
        y=528.0,
        width=300.0,
        height=90.0
    )
    window.resizable(False, False)
    window.mainloop()


main()
