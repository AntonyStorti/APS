import json
import socket
import ssl
import subprocess
from datetime import datetime
from pathlib import Path
from tkinter import Tk, Canvas, Entry, Button, PhotoImage, messagebox
import codicefiscale

OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path(r"./assets/frame1")

server_process = None


def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)


def is_alpha(text):
    """Verifica se il testo contiene solo lettere (alfabetico)"""
    return text.isalpha()


def is_valid_date(date_text):
    """Verifica se la data è valida e se è conforme ai requisiti"""
    try:
        date_of_birth = datetime.strptime(date_text, '%d/%m/%Y')
    except ValueError:
        return False

    today = datetime.today()
    if date_of_birth > today:
        return False

    age = today.year - date_of_birth.year - ((today.month, today.day) < (date_of_birth.month, date_of_birth.day))
    if age > 115:
        return False

    return True


def check_fields(entries):
    """Controlla che tutti i campi siano riempiti e che i campi specifici contengano solo lettere o valori validi"""
    labels = [
        "Nome",
        "Cittadinanza",
        "Statura",
        "Data di nascita",
        "Codice Fiscale",
        "Luogo di nascita",
        "Sesso",
        "Luogo di residenza",
        "Cognome"
    ]

    # Controlla i campi specifici per le lettere
    text_fields_indices = [0, 1, 5, 7, 8]  # Indici dei campi che devono contenere solo lettere
    for index in text_fields_indices:
        if index >= len(entries):
            return f"Errore: l'indice {index} è fuori dal range."
        text = entries[index].get().strip()
        if not text:
            return f"{labels[index]} non può essere vuoto."
        if not is_alpha(text):
            return f"{labels[index]} deve contenere solo lettere."

    # Controllo specifico per il campo "Sesso"
    sex = entries[6].get().strip()
    if sex not in ["M", "F"]:
        return "Il campo 'Sesso' deve essere 'M' o 'F'."

    # Controllo specifico per il campo "Statura"
    stature_text = entries[2].get().strip()
    if not stature_text.isdigit():
        return "Il campo 'Statura' deve contenere solo numeri."
    stature = int(stature_text)
    if stature < 100 or stature > 250:
        return "Il campo 'Statura' deve essere compreso tra 100 e 250 cm."

    codfiscale = entries[4].get().strip()
    if not codicefiscale.isvalid(codfiscale):
        return "Il campo 'Codice Fiscale' deve essere corretto."

    # Controllo specifico per il campo "Data di nascita"
    dob_text = entries[3].get().strip()
    if not is_valid_date(dob_text):
        return "Il campo 'Data di nascita' deve essere una data valida (gg/mm/aaaa) e non deve essere futura o più vecchia di 115 anni."


def show_success_message(entries):
    error_message = check_fields(entries)
    if error_message:
        messagebox.showerror("Errore", error_message)
    else:
        messagebox.showinfo("Successo", "Dati inviati con successo!")


def connessione_TLS(data_dict, window):
    server_address = ('localhost', 4433)  # Indirizzo e porta del server TLS

    try:
        # Crea un contesto SSL con supporto per TLS 1.3
        context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        context.load_verify_locations("../CA/CA_root/intermediate/certs/ca-chain.cert.pem")
        context.load_cert_chain(certfile='../CA/CA_root/intermediate/certs/IPZS_Client.com.cert.pem', keyfile='../CA/CA_root/intermediate/private/IPZS.com.key.pem')
        context.minimum_version = ssl.TLSVersion.TLSv1_3

        context.verify_mode = ssl.CERT_REQUIRED

        # Crea un socket di rete e stabilisci una connessione TLS
        with socket.create_connection(server_address) as sock:
            with context.wrap_socket(sock, server_hostname='localhost') as tls_sock:
                # Converti il dizionario in una stringa JSON
                json_data = json.dumps(data_dict)

                # Invia i dati al server
                tls_sock.sendall(json_data.encode('utf-8'))

                # Ricevi una risposta dal server
                response = tls_sock.recv(1024).decode('utf-8')

                # Mostra un messaggio di successo se la risposta è quella attesa
                if response == 'Hello from TLS server!':
                    messagebox.showinfo("Successo", "La tua carta d'identità è stata creata correttamente!")
                else:
                    messagebox.showwarning("Attenzione", "Risposta inattesa dal server.")

                window.destroy()

    except (socket.error, ssl.SSLError) as e:
        # Gestisci le eccezioni di rete e SSL
        messagebox.showerror("Errore", f"Si è verificato un errore di connessione: {str(e)}")

    finally:
        stop_server()


def avvia_server():
    global server_process
    server_process = subprocess.Popen(["python", "../IPZS/Server.py"])


def stop_server():
    if server_process:
        server_process.terminate()  # Invia un segnale di terminazione
        server_process.wait()       # Attende che il processo termini


def invia_richiesta(entries, window):
    show_success_message(entries)
    labels = [
        "Nome",
        "Cittadinanza",
        "Statura",
        "Data di nascita",
        "Codice Fiscale",
        "Luogo di nascita",
        "Sesso",
        "Luogo di residenza",
        "Cognome"
    ]

    # Assumiamo che entries siano gli entry widget nel tuo ordine
    # e che la lunghezza di entries corrisponda a quella di labels
    data_dict = {label: entry.get().strip() for label, entry in zip(labels, entries)}

    connessione_TLS(data_dict, window)


def main():
    avvia_server()

    window = Tk()
    window.title("Rilascio CIE")

    # Carica l'icona
    icon_image = PhotoImage(file="./icon.png")  # Assicurati che il file esista
    window.iconphoto(True, icon_image)  # Imposta l'icona della finestra

    window.geometry("1000x720")
    window.configure(bg="#FFFFFF")

    canvas = Canvas(
        window,
        bg="#FFFFFF",
        height=720,
        width=1000,
        bd=0,
        highlightthickness=0,
        relief="ridge"
    )

    canvas.place(x=0, y=0)
    image_image_1 = PhotoImage(
        file=relative_to_assets("image_1.png"))
    image_1 = canvas.create_image(
        500.0,
        85.0,
        image=image_image_1
    )

    entry_image_1 = PhotoImage(
        file=relative_to_assets("entry_1.png"))
    entry_bg_1 = canvas.create_image(
        197.0,
        267.0,
        image=entry_image_1
    )
    entry_1 = Entry(
        bd=0,
        bg="#D9D9D9",
        fg="#000716",
        highlightthickness=0
    )
    entry_1.place(
        x=74.0,
        y=235.0,
        width=246.0,
        height=62.0
    )

    entry_image_2 = PhotoImage(
        file=relative_to_assets("entry_2.png"))
    entry_bg_2 = canvas.create_image(
        197.0,
        552.0,
        image=entry_image_2
    )
    entry_2 = Entry(
        bd=0,
        bg="#D9D9D9",
        fg="#000716",
        highlightthickness=0
    )
    entry_2.place(
        x=74.0,
        y=520.0,
        width=246.0,
        height=62.0
    )

    entry_image_3 = PhotoImage(
        file=relative_to_assets("entry_3.png"))
    entry_bg_3 = canvas.create_image(
        801.0,
        403.0,
        image=entry_image_3
    )
    entry_3 = Entry(
        bd=0,
        bg="#D9D9D9",
        fg="#000716",
        highlightthickness=0
    )
    entry_3.place(
        x=678.0,
        y=371.0,
        width=246.0,
        height=62.0
    )

    entry_image_4 = PhotoImage(
        file=relative_to_assets("entry_4.png"))
    entry_bg_4 = canvas.create_image(
        499.0,
        405.0,
        image=entry_image_4
    )
    entry_4 = Entry(
        bd=0,
        bg="#D9D9D9",
        fg="#000716",
        highlightthickness=0
    )
    entry_4.place(
        x=376.0,
        y=373.0,
        width=246.0,
        height=62.0
    )

    entry_image_5 = PhotoImage(
        file=relative_to_assets("entry_5.png"))
    entry_bg_5 = canvas.create_image(
        802.0,
        552.0,
        image=entry_image_5
    )
    entry_5 = Entry(
        bd=0,
        bg="#D9D9D9",
        fg="#000716",
        highlightthickness=0
    )
    entry_5.place(
        x=679.0,
        y=520.0,
        width=246.0,
        height=62.0
    )

    entry_image_6 = PhotoImage(
        file=relative_to_assets("entry_6.png"))
    entry_bg_6 = canvas.create_image(
        197.0,
        403.0,
        image=entry_image_6
    )
    entry_6 = Entry(
        bd=0,
        bg="#D9D9D9",
        fg="#000716",
        highlightthickness=0
    )
    entry_6.place(
        x=74.0,
        y=371.0,
        width=246.0,
        height=62.0
    )

    entry_image_7 = PhotoImage(
        file=relative_to_assets("entry_7.png"))
    entry_bg_7 = canvas.create_image(
        801.0,
        267.0,
        image=entry_image_7
    )
    entry_7 = Entry(
        bd=0,
        bg="#D9D9D9",
        fg="#000716",
        highlightthickness=0
    )
    entry_7.place(
        x=678.0,
        y=235.0,
        width=246.0,
        height=62.0
    )

    entry_image_8 = PhotoImage(
        file=relative_to_assets("entry_8.png"))
    entry_bg_8 = canvas.create_image(
        499.0,
        552.0,
        image=entry_image_8
    )
    entry_8 = Entry(
        bd=0,
        bg="#D9D9D9",
        fg="#000716",
        highlightthickness=0
    )
    entry_8.place(
        x=376.0,
        y=520.0,
        width=246.0,
        height=62.0
    )

    entry_image_9 = PhotoImage(
        file=relative_to_assets("entry_9.png"))
    entry_bg_9 = canvas.create_image(
        499.0,
        267.0,
        image=entry_image_9
    )
    entry_9 = Entry(
        bd=0,
        bg="#D9D9D9",
        fg="#000716",
        highlightthickness=0
    )
    entry_9.place(
        x=376.0,
        y=235.0,
        width=246.0,
        height=62.0
    )

    canvas.create_text(
        74.0,
        197.0,
        anchor="nw",
        text="Nome",
        fill="#000000",
        font=("Inter", 12 * -1)
    )

    canvas.create_text(
        373.0,
        197.0,
        anchor="nw",
        text="Cognome",
        fill="#000000",
        font=("Inter", 12 * -1)
    )

    canvas.create_text(
        74.0,
        336.0,
        anchor="nw",
        text="Luogo di nascita",
        fill="#000000",
        font=("Inter", 12 * -1)
    )

    canvas.create_text(
        373.0,
        336.0,
        anchor="nw",
        text="Data di nascita",
        fill="#000000",
        font=("Inter", 12 * -1)
    )

    canvas.create_text(
        679.0,
        197.0,
        anchor="nw",
        text="Sesso",
        fill="#000000",
        font=("Inter", 12 * -1)
    )

    canvas.create_text(
        685.0,
        472.0,
        anchor="nw",
        text="Codice Fiscale",
        fill="#000000",
        font=("Inter", 12 * -1)
    )

    canvas.create_text(
        679.0,
        333.0,
        anchor="nw",
        text="Statura",
        fill="#000000",
        font=("Inter", 12 * -1)
    )

    canvas.create_text(
        74.0,
        472.0,
        anchor="nw",
        text="Cittadinanza",
        fill="#000000",
        font=("Inter", 12 * -1)
    )

    canvas.create_text(
        376.0,
        475.0,
        anchor="nw",
        text="Luogo di residenza",
        fill="#000000",
        font=("Inter", 12 * -1)
    )

    button_image_1 = PhotoImage(
        file=relative_to_assets("button_1.png"))
    button_1 = Button(
        image=button_image_1,
        borderwidth=0,
        highlightthickness=0,
        command=lambda: invia_richiesta([
            entry_1, entry_2, entry_3, entry_4, entry_5, entry_6, entry_7, entry_8, entry_9
        ], window),
        relief="flat"
    )
    button_1.place(
        x=377.0,
        y=622.0,
        width=246.0,
        height=64.0
    )

    window.resizable(False, False)
    window.mainloop()


main()
