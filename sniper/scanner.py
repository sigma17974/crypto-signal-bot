import asyncio
from typing import Dict

from sniper.telegram import send as notify

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