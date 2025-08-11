from solcx import compile_standard, install_solc
import json
from web3 import Web3
from dotenv import load_dotenv
import os

load_dotenv()

install_solc("0.8.0")

with open("./SimpleStorage.sol", "r") as file:
    simple_storage_file = file.read()

# Compile the Solidity code
compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {
            "SimpleStorage.sol": {
                "content": simple_storage_file
            }
        },
        "settings": {
            "outputSelection": {
                "*": {
                    "*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]
                }
            }
        }
    },
    solc_version="0.8.0"
)

with open("compiled_code.json", "w") as file:
    json.dump(compiled_sol, file)

# Get bytecode
bytecode = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["evm"]["bytecode"]["object"]

# Get ABI
abi = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["abi"]

# Connect to Ganache
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))
chain_id = 1337
my_address = "0x746211ae9E0E657168F7736348db83bCac71bD62"
private_key = os.getenv("PRIVATE_KEY")

# Create the contract in Python
SimpleStorage = w3.eth.contract(abi=abi, bytecode=bytecode)

# Get the latest transaction
nonce = w3.eth.get_transaction_count(my_address)

# Build the transaction
transaction = SimpleStorage.constructor().build_transaction({
    "chainId": chain_id,
    "from": my_address,
    "nonce": nonce
})

# Sign the transaction
signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)

# Send the signed transaction
print("Deploying contract...") 
txn_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)

# Wait for the block confirmation
txn_receipt = w3.eth.wait_for_transaction_receipt(txn_hash)
print("Deployed!")

# Work with the contract
simple_storage = w3.eth.contract(
    address=txn_receipt.contractAddress,
    abi=abi
)

# Call -> Simulate making the call and getting the result without state change
# Transaction -> Actually make a state change

# Call the retrieve() function
print(simple_storage.functions.retrieve().call())

# Set a new value for favorite number
print("Updating contract...")
store_transaction = simple_storage.functions.store(15).build_transaction({
    "chainId": chain_id,
    "from": my_address,
    "nonce": nonce + 1
})

signed_store_txn = w3.eth.account.sign_transaction(store_transaction, private_key=private_key)
txn_store_hash = w3.eth.send_raw_transaction(signed_store_txn.raw_transaction)
txn_store_receipt = w3.eth.wait_for_transaction_receipt(txn_store_hash)
print("Updated!")
print(simple_storage.functions.retrieve().call())