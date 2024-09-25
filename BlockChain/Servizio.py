from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization


def servizio(MyContract, w3, numero_documento, chiave_pubblica, risultato):

    SERVIZIO = w3.eth.accounts[1]
    w3.eth.default_account = SERVIZIO

    # Carica la chiave pubblica PEM
    public_key = serialization.load_pem_public_key(
        chiave_pubblica.encode(),
        backend=default_backend()
    )

    # Estrai i byte della chiave pubblica
    public_numbers = public_key.public_numbers()
    x = public_numbers.x
    y = public_numbers.y

    # Converti in esadecimale per ottenere un formato leggibile
    pub_key_hex = f"04{x:064x}{y:064x}"

    chiave_pubblica = bytes.fromhex(pub_key_hex)

    try:
        # Call the function and print the result
        result = MyContract.functions.verifyKey(numero_documento, chiave_pubblica).call()
        risultato['result'] = result
    except Exception as e:
        print(f"Error interacting with contract: {e}")