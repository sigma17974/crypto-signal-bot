# 🏹 Crypto Sniper Bot

An automated PancakeSwap/Uniswap-V2 “sniper” that watches target pairs and fires ultra-fast buy transactions when price or liquidity conditions are met.

Built on top of Web3.py, Flask & APScheduler.  Ships ready for Railway/Fly.io, but can be deployed to any Linux VPS.

---

## ✨ Features

* Pair watcher with configurable **price / liquidity triggers**
* Automatic **gas multiplier** & retry logic
* **Slippage-safe** swapExactTokensForTokens route
* **Position tracker** so the bot never buys twice by mistake – persisted to *positions.json*
* **Telegram notifications** for scanner start, trigger hits, swap success & failures
* Health-check web interface (`/` & `/admin`) so you can keep it alive with UptimeRobot

---

## 📦 Directory

```text
├─ main.py              # Flask server + orchestrator
├─ sniper/
│   ├─ config.py        # Env + constants
│   ├─ scanner.py       # PairWatcherScanner
│   ├─ trader.py        # Builds / signs / sends swaps
│   ├─ telegram.py      # Telegram helper
│   ├─ state.py         # PositionTracker
│   └─ __init__.py
├─ requirements.txt     # Python deps
├─ .env.example         # Copy → .env and fill secrets
└─ README.md            # This file
```

---

## 🚀 Quick start

1. **Clone** the repo & install deps:
   ```bash
   git clone <your_repo>
   cd <your_repo>
   python -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. **Configure env vars** – copy `.env.example` to `.env` and fill:
   * `PRIVATE_KEY` – hot wallet with funds (⚠️ max you can afford to lose)
   * `RPC_URL` – HTTPS endpoint (BSC, Ankr, QuickNode …)
   * `TELEGRAM_TOKEN` & `TELEGRAM_CHAT_ID` – optional but nice
3. **Define targets** – open `sniper/config.py → TARGETS` and add real pair / token addresses, amount, trigger price, min liquidity.
4. **Run** the bot:
   ```bash
   python main.py
   ```
5. Keep it alive – e.g. **Railway**: set `CMD` to `python main.py`; add env vars through the UI and deploy.

---

## 🔑 Environment variables

| Var | Description |
|-----|-------------|
| `PRIVATE_KEY` | Hex string of wallet private key (0x…) |
| `RPC_URL` | HTTPS RPC endpoint |
| `TELEGRAM_TOKEN` | Bot token from @BotFather |
| `TELEGRAM_CHAT_ID` | Chat ID to send messages |
| `GAS_MULTIPLIER` | Multiplier on current network gas price (default 1.2) |
| `POLL_INTERVAL` | Seconds between reserve polls (default 3) |
| `ROUTER_ADDRESS` | DEX router, default PancakeSwap v2 |
| `WRAPPED_NATIVE` | Wrapped native token (WBNB, WETH …) |
| `POSITIONS_FILE` | Where open positions are stored |

---

## 🛡️ Safety

* Trades are only executed **once per pair** – guarded by in-memory + disk PositionTracker.
* Input validation on addresses, amounts & slippage keeps obvious mistakes from sending txs.
* Unlimited token allowance is granted *once* to the router – you can revoke anytime with BSCScan.
* Use a dedicated **hot wallet**; never the one holding your life savings.

---

## 🧩 Extending

* **Mempool sniping** – add a `PendingTxScanner` to `sniper/scanner.py` that subscribes to `eth_newPendingTransactionFilter`.
* **Native→Token routes** – change path building in `Trader._sync_execute`.
* **Sell logic** – add SELL direction & corresponding router method.
* **Unit tests** – PyTest + Brownie for forked-mainnet simulation.

---

## 📜 Licence

MIT – free to use, modify & distribute.  **No warranties.** Use at your own risk.
