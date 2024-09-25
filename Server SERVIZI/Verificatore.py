from ecdsa.curves import NIST256p
from ecdsa.keys import VerifyingKey
from hashlib import sha256


def verifier(pk_pem, u, c, z):
    # Parametri iniziali (curva e generatore)
    curve = NIST256p
    g = curve.generator
    q = curve.order

    # Carica la chiave pubblica
    pk = VerifyingKey.from_pem(pk_pem)

    bool = schnorr_validate(u, pk)

    if bool == False:
        return False

    # Step 1: Genera la sfida deterministica c usando la Fiat-Shamir heuristic
    # Concatenate (g, q, pk, u) e hash il risultato
    g_bytes = g.to_bytes()
    q_bytes = q.to_bytes(32, 'big')  # Assicurati che q abbia una lunghezza fissa
    pk_bytes = pk.to_string()
    u_bytes = u.to_bytes()

    # Concatena i byte in ordine: g, q, pk, u
    message = g_bytes + q_bytes + pk_bytes + u_bytes
    computed_c = int.from_bytes(sha256(message).digest(), 'big') % q

    # Verifica se la sfida c calcolata è la stessa di quella ricevuta
    if c != computed_c:
        return False  # La sfida non corrisponde

    # Step 2: Calcola z*g e verifica che sia uguale a u + c * pk
    g_z = z * g  # Calcola z*g
    u_plus_c_pk = u + c * pk.pubkey.point  # Calcola u + c * pk

    # Verifica
    return g_z == u_plus_c_pk


def schnorr_validate(u, pk):
    if u == 0 or pk == 0:
        return False
