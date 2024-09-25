from ecdsa.keys import SigningKey
from ecdsa.curves import NIST256p
from hashlib import sha256
import os


def prover(private_key_pem):
    # Parametri iniziali (curva e generatore)
    curve = NIST256p
    g = curve.generator
    q = curve.order

    # Carica la chiave privata
    private_key = SigningKey.from_pem(private_key_pem)
    pk = private_key.get_verifying_key()

    # Step 1: Seleziona r casuale
    r = int.from_bytes(os.urandom(32), 'big') % q

    # Calcola u = r*g
    u = r * g

    # Step 2: Genera la sfida deterministica c usando la Fiat-Shamir heuristic
    # Concatenate (g, q, pk, u) e hash il risultato
    g_bytes = g.to_bytes()
    q_bytes = q.to_bytes(32, 'big')  # Assicurati che q abbia una lunghezza fissa
    pk_bytes = pk.to_string()
    u_bytes = u.to_bytes()

    # Concatena i byte in ordine: g, q, pk, u
    message = g_bytes + q_bytes + pk_bytes + u_bytes

    c = int.from_bytes(sha256(message).digest(), 'big') % q

    # Step 3: Calcola la risposta z = r + c * sk (mod q)
    z = (r + c * private_key.privkey.secret_multiplier) % q

    # Restituisce u, c, e z come prova
    return u, c, z
