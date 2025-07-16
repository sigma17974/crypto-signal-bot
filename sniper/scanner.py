import asyncio
from typing import Dict

from sniper.telegram import send as notify

# --- UniswapV2/PancakeSwap Pair ABI subset ---
PAIR_ABI = [
    {
        "constant": True,
        "inputs": [],
        "name": "getReserves",
        "outputs": [
            {"internalType": "uint112", "name": "_reserve0", "type": "uint112"},
            {"internalType": "uint112", "name": "_reserve1", "type": "uint112"},
            {"internalType": "uint32", "name": "_blockTimestampLast", "type": "uint32"},
        ],
        "payable": False,
        "stateMutability": "view",
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [],
        "name": "token0",
        "outputs": [{"internalType": "address", "name": "", "type": "address"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [],
        "name": "token1",
        "outputs": [{"internalType": "address", "name": "", "type": "address"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [],
        "name": "totalSupply",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function",
    },
]

ERC20_ABI_DECIMALS = [
    {
        "constant": True,
        "inputs": [],
        "name": "decimals",
        "outputs": [{"internalType": "uint8", "name": "", "type": "uint8"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function",
    }
]

from functools import lru_cache
from sniper import config
from sniper.state import PositionTracker
from web3 import Web3

class PairWatcherScanner:
    """Watches specified pair reserves to trigger price/liquidity conditions."""

    def __init__(self, queue: asyncio.Queue, w3: Web3 | None = None):
        self.queue = queue
        self.w3 = w3 or config.w3
        self._running = False
        # Cache contract objects
        self._pair_contracts: dict[str, any] = {}
        self._triggered: set[str] = set()  # pair addresses already emitted
        self.positions = PositionTracker()

    async def start(self) -> None:
        notify("🔍 PairWatcherScanner started")
        self._running = True
        while self._running:
            await self._poll_once()
            await asyncio.sleep(config.POLL_INTERVAL)

    def stop(self) -> None:
        self._running = False

    async def _poll_once(self):
        for target in config.TARGETS:
            pair_addr = Web3.to_checksum_address(target["pair"])
            if pair_addr in self._triggered or self.positions.has(pair_addr):
                continue  # already triggered or executed in previous session

            pair = self._get_pair_contract(pair_addr)
            try:
                reserves = pair.functions.getReserves().call()
                reserve0, reserve1 = reserves[0], reserves[1]
            except Exception as exc:
                print(f"Error reading reserves for {pair_addr}: {exc}")
                continue

            # Determine which token is base vs quote
            token0 = pair.functions.token0().call()
            token1 = pair.functions.token1().call()
            base_token = Web3.to_checksum_address(target.get("base_token", token0))
            quote_token = Web3.to_checksum_address(target.get("quote_token", token1))

            if token0 == base_token:
                price = reserve1 / reserve0 if reserve0 else float("inf")
            else:
                price = reserve0 / reserve1 if reserve1 else float("inf")

            liquidity_quote = reserve1 if token1 == quote_token else reserve0

            # Apply simple decimals fix (assume both tokens 18). TODO: fetch decimals

            direction = target.get("direction", "BUY").upper()
            trigger_price = target["trigger_price"]
            min_liq = target.get("min_liquidity", 0)

            condition_met = False
            if direction == "BUY" and price <= trigger_price:
                condition_met = True
            elif direction == "SELL" and price >= trigger_price:
                condition_met = True

            if condition_met and liquidity_quote >= min_liq:
                await self.queue.put(target)
                self._triggered.add(pair_addr)
                notify(
                    f"🎯 Target hit ({target.get('name', pair_addr)}): price={price:.6f}, liq={liquidity_quote:.2f}"
                )

    def _get_pair_contract(self, pair_addr: str):
        if pair_addr not in self._pair_contracts:
            self._pair_contracts[pair_addr] = self.w3.eth.contract(
                address=pair_addr, abi=PAIR_ABI
            )
        return self._pair_contracts[pair_addr]

# Keep DummyScanner for tests

class DummyScanner:
    """Placeholder scanner that periodically emits dummy targets."""

    def __init__(self, queue: asyncio.Queue):
        self.queue = queue
        self._running = False

    async def start(self) -> None:
        self._running = True
        notify("🚀 Scanner started (dummy mode)")
        while self._running:
            await asyncio.sleep(5)
            dummy_target: Dict = {"type": "DUMMY", "msg": "pretend target"}
            await self.queue.put(dummy_target)
            notify(f"New dummy target emitted: {dummy_target}")

    def stop(self) -> None:
        self._running = False