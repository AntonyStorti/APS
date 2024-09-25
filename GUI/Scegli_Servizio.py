import subprocess
from pathlib import Path
from tkinter import Tk, Canvas, Button, PhotoImage
import pygetwindow as gw

OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path(r"./assets/frame3")


def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)


def run_Accesso_Poker():
    active_window = gw.getActiveWindow()
    active_window.close()
    # Esegue il secondo script come un nuovo processo
    subprocess.Popen(["python", "./Accesso_Poker.py"])


def run_Accesso_RdC():
    active_window = gw.getActiveWindow()
    active_window.close()
    # Esegue il secondo script come un nuovo processo
    subprocess.Popen(["python", "./Accesso_RdC.py"])


def main():
    window = Tk()
    window.title("Scegli Servizio")

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
        499.0,
        90.0,
        image=image_image_1
    )

    canvas.create_rectangle(
        0.0,
        185.0,
        1000.0,
        201.0,
        fill="#000000",
        outline="")

    button_image_1 = PhotoImage(
        file=relative_to_assets("button_1.png"))
    button_1 = Button(
        image=button_image_1,
        borderwidth=0,
        highlightthickness=0,
        command=run_Accesso_Poker,
        relief="flat"
    )
    button_1.place(
        x=48.0,
        y=317.0,
        width=372.0,
        height=266.0
    )

    button_image_2 = PhotoImage(
        file=relative_to_assets("button_2.png"))
    button_2 = Button(
        image=button_image_2,
        borderwidth=0,
        highlightthickness=0,
        command=run_Accesso_RdC,
        relief="flat"
    )
    button_2.place(
        x=541.0,
        y=347.0,
        width=399.0,
        height=205.0
    )
    window.resizable(False, False)
    window.mainloop()


main()
