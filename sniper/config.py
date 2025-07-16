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

# Poll interval (seconds) for price/liquidity watcher
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", "3"))

# Router (PancakeSwap v2 on BSC) – override with env var if needed
ROUTER_ADDRESS = os.getenv("ROUTER_ADDRESS", "0x10ED43C718714eb63d5aA57B78B54704E256024E")

# Wrapped native token (WBNB for BSC)
WRAPPED_NATIVE = os.getenv("WRAPPED_NATIVE", "0xBB4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c")

# Example targets – replace with real pair addresses & parameters
# Each dict must contain at minimum:
#   pair:   PancakeSwap/UniswapV2 pair address
#   trigger_price: price of base token in quote token units at which to trigger
#   amount_in: amount of quote token to spend when triggered
# Optional:
#   min_liquidity: minimum total liquidity (quote-token units) required
#   direction: "BUY" (<= trigger_price) or "SELL" (>= trigger_price)
TARGETS: list[dict] = [
    {
        "name": "Example BNB/USDT",
        "pair": "0x0000000000000000000000000000000000000000",  # TODO: real address
        "base_token": "0x0000000000000000000000000000000000000000",  # WBNB
        "quote_token": "0x0000000000000000000000000000000000000000",  # USDT
        "trigger_price": 500.0,
        "amount_in": 0.1,
        "min_liquidity": 10000.0,
        "direction": "BUY",
    }
]