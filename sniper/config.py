import os
from web3 import Web3

RPC_URL = os.getenv("RPC_URL", "https://bsc-dataseed.binance.org")
PRIVATE_KEY = os.getenv("PRIVATE_KEY", "")

w3 = Web3(Web3.HTTPProvider(RPC_URL))

# Wallet address derived from private key if provided
WALLET_ADDRESS = (
    w3.eth.account.from_key(PRIVATE_KEY).address if PRIVATE_KEY else ""
)

# Gas price multiplier applied to current network gas price
GAS_MULTIPLIER = float(os.getenv("GAS_MULTIPLIER", "1.2"))

# Targets list will be filled with dictionaries that describe each snipe config
TARGETS: list[dict] = []