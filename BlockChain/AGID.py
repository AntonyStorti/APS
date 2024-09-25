import csv
import threading
import solcx
from eth_tester import EthereumTester
from web3 import Web3
from web3.providers.eth_tester import EthereumTesterProvider
from solcx import compile_source
from BlockChain.Servizio import servizio


def set_Blockchain(MyContract):
    nome_file = '../BlockChain/Credenziali.csv'
    documenti = []

    # Apri il file CSV in modalità lettura
    with open(nome_file, mode='r', newline='') as file:
        reader = csv.DictReader(file)  # Usa DictReader per leggere in forma di dizionario

        # Leggi ogni riga e aggiungila alla lista come dizionario
        for row in reader:
            documenti.append({'Numero Documento': row['Numero Documento'], 'Chiave Pubblica': row['Chiave Pubblica']})

    for documento in documenti:
        numero_documento = documento['Numero Documento']
        chiave_pubblica_hex = documento['Chiave Pubblica']
        chiave_pubblica = bytes.fromhex(chiave_pubblica_hex)

        try:
            result = MyContract.functions.addKey(numero_documento, chiave_pubblica).transact()
        except Exception as e:
            print(f"Error interacting with contract: {e}")


def stampa_blocchi(w3):
    # Stampa tutti i blocchi fino all'ultimo
    latest_block_number = w3.eth.block_number  # Ottieni il numero dell'ultimo blocco

    print("\nAll Blocks:")
    for block_number in range(latest_block_number + 1):
        block = w3.eth.get_block(block_number)
        print(f"\nBlock Number: {block['number']}")
        print(f"Block Hash: {block['hash'].hex()}")
        # print(f"Miner: {block['miner']}")
        print(f"Timestamp: {block['timestamp']}")
        print(f"Gas Used: {block['gasUsed']}")
        print(f"Transactions: {[tx.hex() for tx in block['transactions']]}")


def Agid(MyContract, w3):

    AGID = w3.eth.accounts[0]
    w3.eth.default_account = AGID

    set_Blockchain(MyContract)

    stampa_blocchi(w3)


def blockchain(numero_documento, chiave_pubblica):

    # Install and set Solidity compiler version
    solcx.install_solc('0.8.0')
    solcx.set_solc_version('0.8.0')

    # Read the Solidity contract from file
    with open("../BlockChain/Smart_Contract.sol", "r") as file:
        contract_source_code = file.read()

    # Compile the contract
    compiled_sol = compile_source(
        contract_source_code,
        output_values=["abi", "bin"]
    )

    # Get the compiled contract
    contract_id, contract_interface = compiled_sol.popitem()

    # ABI and Bytecode
    abi = contract_interface['abi']
    bytecode = contract_interface['bin']

    # Set up Ethereum Tester
    eth_tester = EthereumTester()
    provider = EthereumTesterProvider(eth_tester)
    w3 = Web3(provider)

    # Define accounts A and B
    AGID = w3.eth.accounts[0]
    SERVIZIO = w3.eth.accounts[1]

    print(f"Account A: {AGID}")
    print(f"Account B: {SERVIZIO}")

    # Set the default account
    w3.eth.default_account = AGID

    # Deploy the contract with Account A
    MyContract = w3.eth.contract(abi=abi, bytecode=bytecode)
    tx_hash = MyContract.constructor().transact({'from': AGID})
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    # Get the deployed contract address
    contract_address = tx_receipt.contractAddress
    print(f"Contract deployed at address: {contract_address}")

    # Create contract instance using the deployed address
    MyContract = w3.eth.contract(address=contract_address, abi=abi)

    risultato = {}

    first_thread = threading.Thread(target=Agid(MyContract, w3))
    first_thread.start()

    # Avvia il secondo script in un altro thread
    second_thread = threading.Thread(target=servizio(MyContract, w3, numero_documento, chiave_pubblica, risultato))
    second_thread.start()

    # Attendi che entrambi i thread finiscano
    first_thread.join()
    second_thread.join()

    result = risultato.get('result')

    return result
