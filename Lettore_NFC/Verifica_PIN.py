import subprocess
import tkinter as tk
from tkinter import messagebox
import pandas as pd
import os


def verifica_PIN(numero_documento, window):
    def lettore_NFC():
        pin_inserito = entry_pin.get().strip()

        file_path = '../Lettore_NFC/PIN.csv'

        if not os.path.exists(file_path):
            messagebox.showerror("Errore", "Il file CSV non è stato trovato!")
            return

        try:
            # Leggi il CSV trattando i PIN come stringhe
            df = pd.read_csv(file_path, dtype={'numero_documento': str, 'PIN': str})

            # Filtra il DataFrame per il numero di documento
            filtered_df = df[df['numero_documento'] == numero_documento]

            # Verifica se il PIN inserito è presente per il numero di documento fornito
            if pin_inserito in filtered_df['PIN'].values:
                messagebox.showinfo("Successo", "PIN corretto!")
                window.destroy()
                subprocess.Popen(["python", "./Scegli_Credenziale.py"])
            else:
                messagebox.showerror("Errore", "PIN non corretto per il numero di documento fornito!")
        except pd.errors.EmptyDataError:
            messagebox.showerror("Errore", "Il file CSV è vuoto o malformato.")
        except Exception as e:
            messagebox.showerror("Errore", f"Si è verificato un errore: {e}")
        finally:
            root.destroy()

    # Configura la GUI
    root = tk.Tk()
    root.title("Verifica PIN CIE")

    # Imposta la dimensione della finestra
    root.geometry("300x150")  # Larghezza x Altezza

    # Crea e posiziona i widget
    label = tk.Label(root, text="Inserisci il PIN:")
    label.pack(pady=10)

    entry_pin = tk.Entry(root, show="*")
    entry_pin.pack(pady=5)

    verifica_button = tk.Button(root, text="Verifica PIN", command=lettore_NFC)
    verifica_button.pack(pady=20)

    # Avvia il loop principale
    root.mainloop()
