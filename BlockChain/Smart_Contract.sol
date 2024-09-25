pragma solidity ^0.8.0;

contract AGID_pkManager {
    mapping(string => bytes[]) private documentKeys;
    address private owner;

    event KeyAdded(string documentNumber, bytes publicKey);
    event KeyRemoved(string documentNumber, bytes publicKey);

    modifier onlyOwner() {
        require(msg.sender == owner, "Accesso negato: solo il proprietario puo' eseguire questa operazione.");
        _;
    }

    modifier documentExists(string calldata documentNumber) {
        require(documentKeys[documentNumber].length > 0, "Il documento non esiste.");
        _;
    }

    constructor() {
        owner = msg.sender; // Imposta l'indirizzo del creatore come proprietario
    }

    // Funzione per aggiungere la chiave pubblica (solo per il proprietario)
    function addKey(string calldata documentNumber, bytes calldata publicKey) external onlyOwner {
        require(!keyExists(documentNumber, publicKey), "La chiave e' gia' associata a questo documento.");
        documentKeys[documentNumber].push(publicKey);
        emit KeyAdded(documentNumber, publicKey);
    }

    // Funzione per rimuovere la chiave pubblica (solo per il proprietario)
    function removeKey(string calldata documentNumber, bytes calldata publicKey) external onlyOwner documentExists(documentNumber) {
        uint index = findKeyIndex(documentNumber, publicKey);
        require(index < documentKeys[documentNumber].length, "Chiave non trovata.");
        documentKeys[documentNumber][index] = documentKeys[documentNumber][documentKeys[documentNumber].length - 1];
        documentKeys[documentNumber].pop();
        emit KeyRemoved(documentNumber, publicKey);
    }

    // Funzione interna per controllare se la chiave pubblica esiste già per un documento
    function keyExists(string calldata documentNumber, bytes memory publicKey) internal view returns (bool) {
        bytes[] storage keys = documentKeys[documentNumber];
        for (uint i = 0; i < keys.length; i++) {
            // Confronta gli elementi copiando i byte dallo storage nella memory
            if (compareBytes(keys[i], publicKey)) {
                return true;
            }
        }
        return false;
    }

    // Funzione interna per trovare l'indice della chiave pubblica
    function findKeyIndex(string calldata documentNumber, bytes memory publicKey) internal view returns (uint) {
        bytes[] storage keys = documentKeys[documentNumber];
        for (uint i = 0; i < keys.length; i++) {
            // Confronta gli elementi copiando i byte dallo storage nella memory
            if (compareBytes(keys[i], publicKey)) {
                return i;
            }
        }
        revert("Chiave non trovata.");
    }

    // Funzione interna per confrontare byte per byte
    function compareBytes(bytes storage a, bytes memory b) internal view returns (bool) {
        if (a.length != b.length) {
            return false; // Lunghezze diverse significano che sono diversi
        }

        for (uint i = 0; i < a.length; i++) {
            if (a[i] != b[i]) {
                return false; // Se differiscono per un solo byte, sono diversi
            }
        }
        return true; // Sono uguali
    }

    ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    // Funzione per verificare se la chiave pubblica esiste per un determinato documento (unica accessibile a tutti!)
    function verifyKey(string calldata documentNumber, bytes calldata publicKey) external view returns (bool) {
        return keyExists(documentNumber, publicKey);
    }
}
