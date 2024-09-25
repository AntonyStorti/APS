import subprocess
from pathlib import Path
from tkinter import Tk, Canvas, Button, PhotoImage

OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path(r"./assets/frame0")


def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)


def run_Rilascio_CIE():
    # Esegue il secondo script come un nuovo processo
    subprocess.Popen(["python", "./Rilascio_CIE.py"])


def run_Carica_CIE():
    # Esegue il secondo script come un nuovo processo
    subprocess.Popen(["python", "./Carica_CIE.py"])


def run_Scegli_Servizio():
    # Esegue il secondo script come un nuovo processo
    subprocess.Popen(["python", "./Scegli_Servizio.py"])


def main():

    window = Tk()
    window.title("AuthPass")

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

    button_image_1 = PhotoImage(
        file=relative_to_assets("button_1.png"))
    button_1 = Button(
        image=button_image_1,
        borderwidth=0,
        highlightthickness=0,
        command=run_Rilascio_CIE,
        relief="flat"
    )
    button_1.place(
        x=250.0,
        y=305.0,
        width=500.0,
        height=110.0
    )

    button_image_2 = PhotoImage(
        file=relative_to_assets("button_2.png"))
    button_2 = Button(
        image=button_image_2,
        borderwidth=0,
        highlightthickness=0,
        command=run_Carica_CIE,
        relief="flat"
    )
    button_2.place(
        x=175.0,
        y=424.0,
        width=650.0,
        height=140.0
    )

    button_image_3 = PhotoImage(
        file=relative_to_assets("button_3.png"))
    button_3 = Button(
        image=button_image_3,
        borderwidth=0,
        highlightthickness=0,
        command=run_Scegli_Servizio,
        relief="flat"
    )
    button_3.place(
        x=175.0,
        y=564.0,
        width=650.0,
        height=140.0
    )

    canvas.create_rectangle(
        0.0,
        0.0,
        1312.0,
        242.0,
        fill="#0303FF",
        outline=""
    )

    image_image_1 = PhotoImage(
        file=relative_to_assets("image_1.png"))
    image_1 = canvas.create_image(
        500.0,
        121.0,
        image=image_image_1
    )

    window.resizable(False, False)
    window.mainloop()


# Avvia l'interfaccia principale
main()
