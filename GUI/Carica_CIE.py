import socket
import ssl
import subprocess
from pathlib import Path
from tkinter import Tk, Canvas, Button, PhotoImage, filedialog, messagebox
from Lettore_NFC.Verifica_PIN import verifica_PIN

OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path(r"./assets/frame4")
file_path = Path(__file__)

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


def connessione_TLS(window):
    server_address = ('localhost', 4434)  # Indirizzo e porta del server TLS

    try:
        # Crea un contesto SSL con supporto per TLS 1.3
        context = ssl.create_default_context()
        context.load_verify_locations("../CA/CA_root/CREDENZIALI_intermediate/certs/ca-chain.cert.pem")
        context.minimum_version = ssl.TLSVersion.TLSv1_3

        # Crea un socket di rete e stabilisci una connessione TLS
        with socket.create_connection(server_address) as sock:
            with context.wrap_socket(sock, server_hostname='localhost') as tls_sock:
                certificato = file_path
                with open(certificato, "rb") as cert_file:
                    cert_data = cert_file.read()

                # Invia i dati al server
                tls_sock.sendall(cert_data)

                # Ricevi una risposta dal server
                response = tls_sock.recv(1024).decode('utf-8')

                # Mostra un messaggio di successo se la risposta è quella attesa
                if response == 'Hello from TLS server!':
                    messagebox.showinfo("Successo", "La tua carta d'identità è stata caricata e verificata correttamente!")
                    numero_documento = recupera_numero_documento()

                    verifica_PIN(numero_documento, window)

                else:
                    messagebox.showerror("Errore", response)
                    window.destroy()

    except (socket.error, ssl.SSLError) as e:
        # Gestisci le eccezioni di rete e SSL
        messagebox.showerror("Errore", f"Si è verificato un errore di connessione: {str(e)}")

    finally:
        stop_server()


def avvia_server():
    global server_process
    server_process = subprocess.Popen(["python", "../Server CREDENZIALI/Server_Carica_CIE.py"])


def stop_server():
    if server_process:
        server_process.terminate()  # Invia un segnale di terminazione
        server_process.wait()       # Attende che il processo termini


def main():
    avvia_server()

    window = Tk()
    window.title("Carica CIE")

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
        22.0,
        11.0,
        anchor="nw",
        text="Ottieni la tua credenziale...",
        fill="#000000",
        font=("Inter Black", 40 * -1)
    )

    canvas.create_rectangle(
        0.0,
        80.0,
        1000.0,
        96.0,
        fill="#FF0000",
        outline=""
    )

    canvas.create_text(
        214.0,
        298.0,
        anchor="nw",
        text="Carica la tua CIE:",
        fill="#000000",
        font=("Inter ExtraLight", 40 * -1)
    )

    button_image_1 = PhotoImage(
        file=relative_to_assets("button_1.png"))
    button_1 = Button(
        image=button_image_1,
        borderwidth=0,
        highlightthickness=0,
        command=choose_file,  # Modifica per aprire la finestra di dialogo
        relief="flat"
    )
    button_1.place(
        x=624.0,
        y=298.0,
        width=246.0,
        height=64.0
    )

    button_image_2 = PhotoImage(
        file=relative_to_assets("button_2.png"))
    button_2 = Button(
        image=button_image_2,
        borderwidth=0,
        highlightthickness=0,
        command=lambda: connessione_TLS(window),
        relief="flat"
    )
    button_2.place(
        x=350.0,
        y=542.0,
        width=300.0,
        height=90.0
    )

    window.resizable(False, False)
    window.mainloop()


main()
