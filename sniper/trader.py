import asyncio
import time
from decimal import Decimal
from typing import List

from tenacity import retry, stop_after_attempt, wait_fixed
from web3 import Web3
from web3.exceptions import ContractLogicError

from sniper import config
from sniper.telegram import send as notify
from sniper.state import PositionTracker


# --- PancakeSwap / UniswapV2 Router ABI subset ---
ROUTER_ABI = [
    {
        "name": "swapExactTokensForTokens",
        "outputs": [
            {"type": "uint256[]", "name": "amounts"}
        ],
        "inputs": [
            {"type": "uint256", "name": "amountIn"},
            {"type": "uint256", "name": "amountOutMin"},
            {"type": "address[]", "name": "path"},
            {"type": "address", "name": "to"},
            {"type": "uint256", "name": "deadline"},
        ],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "name": "getAmountsOut",
        "outputs": [{"type": "uint256[]", "name": "amounts"}],
        "inputs": [
            {"type": "uint256", "name": "amountIn"},
            {"type": "address[]", "name": "path"},
        ],
        "stateMutability": "view",
        "type": "function",
    },
]


ERC20_ABI = [
    {
        "constant": False,
        "inputs": [
            {"internalType": "address", "name": "spender", "type": "address"},
            {"internalType": "uint256", "name": "amount", "type": "uint256"},
        ],
        "name": "approve",
        "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
        "payable": False,
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [
            {"internalType": "address", "name": "owner", "type": "address"},
            {"internalType": "address", "name": "spender", "type": "address"},
        ],
        "name": "allowance",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [],
        "name": "decimals",
        "outputs": [{"internalType": "uint8", "name": "", "type": "uint8"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function",
    },
]


class Trader:
    """Builds, signs and submits swap transactions via the router."""

    def __init__(self, w3: Web3 | None = None):
        self.w3 = w3 or config.w3
        if not config.PRIVATE_KEY:
            raise RuntimeError("PRIVATE_KEY must be set for trading")
        self.account = self.w3.eth.account.from_key(config.PRIVATE_KEY)
        self.positions = PositionTracker()
        self.router = self.w3.eth.contract(
            address=Web3.to_checksum_address(config.ROUTER_ADDRESS), abi=ROUTER_ABI
        )

    async def execute(self, target: dict) -> None:
        """Execute swap based on target description."""

        try:
            tx_hash = await asyncio.get_event_loop().run_in_executor(
                None, self._sync_execute, target
            )
            notify(f"✅ Swap sent: {tx_hash.hex()}")

            # Mark position executed
            self.positions.add(target["pair"])

        except Exception as exc:
            notify(f"❌ Swap failed: {exc}")

    # ---------------- internal sync helpers ----------------

    def _sync_execute(self, target: dict):
        # Input validation
        for addr_key in ("quote_token", "base_token", "pair"):
            if not Web3.is_address(target[addr_key]):
                raise ValueError(f"Invalid address for {addr_key}: {target[addr_key]}")

        if self.positions.has(target["pair"]):
            raise RuntimeError("Position already executed for this pair")

        if target["amount_in"] <= 0:
            raise ValueError("amount_in must be positive")

        slippage_val = target.get("slippage", 0.5)
        if not (0 < slippage_val < 50):
            raise ValueError("slippage must be between 0 and 50 percent")

        path = [Web3.to_checksum_address(target["quote_token"]), Web3.to_checksum_address(target["base_token"])]

        amount_in_wei = self._to_wei(target["amount_in"], path[0])

        # Ensure allowance for ERC20 input token
        self._ensure_allowance(path[0], amount_in_wei)

        # Slippage
        slippage_pct = Decimal(str(target.get("slippage", 0.5)))  # percent

        amounts = self.router.functions.getAmountsOut(amount_in_wei, path).call()
        amount_out_min = int(Decimal(amounts[-1]) * (Decimal(1) - slippage_pct / Decimal(100)))

        # Build tx
        deadline = int(time.time()) + 60  # 1 minute deadline
        tx = self.router.functions.swapExactTokensForTokens(
            amount_in_wei,
            amount_out_min,
            path,
            self.account.address,
            deadline,
        ).build_transaction(self._build_tx_params())

        signed = self.account.sign_transaction(tx)

        # Send tx with retry
        return self._send_raw_transaction_with_retry(signed.rawTransaction)

    def _build_tx_params(self):
        nonce = self.w3.eth.get_transaction_count(self.account.address)
        gas_price = int(self.w3.eth.gas_price * config.GAS_MULTIPLIER)
        return {
            "from": self.account.address,
            "nonce": nonce,
            "gas": 300000,  # estimate upper bound
            "gasPrice": gas_price,
        }

    def _send_raw_transaction_with_retry(self, raw_tx):

        @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
        def _inner():
            return self.w3.eth.send_raw_transaction(raw_tx)

        tx_hash = _inner()
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=180)
        if receipt.status != 1:
            raise RuntimeError(f"Tx reverted: {tx_hash.hex()}")
        return tx_hash

    def _ensure_allowance(self, token_addr: str, amount: int):
        """Approve router to spend token if allowance is insufficient."""
        token = self.w3.eth.contract(address=token_addr, abi=ERC20_ABI)
        allowance = token.functions.allowance(self.account.address, config.ROUTER_ADDRESS).call()
        if allowance >= amount:
            return

        # Build approve tx for large allowance
        approve_tx = token.functions.approve(config.ROUTER_ADDRESS, 2 ** 256 - 1).build_transaction(
            self._build_tx_params()
        )
        signed = self.account.sign_transaction(approve_tx)
        tx_hash = self.w3.eth.send_raw_transaction(signed.rawTransaction)
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
        if receipt.status != 1:
            raise RuntimeError("Approve failed")

    def _to_wei(self, amount: float, token_addr: str) -> int:
        token = self.w3.eth.contract(address=token_addr, abi=ERC20_ABI)
        try:
            decimals = token.functions.decimals().call()
        except ContractLogicError:
            decimals = 18
        return int(Decimal(str(amount)) * (10 ** decimals))