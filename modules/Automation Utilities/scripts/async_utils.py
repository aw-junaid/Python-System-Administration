#!/usr/bin/env python3
"""
async_utils.py
--------------------
Non-blocking concurrency helpers built on `asyncio`. Includes a
gather-with-concurrency-limit helper (asyncio.gather alone has no
built-in way to cap how many coroutines run at once, which matters
when you're calling a rate-limited API).

Usage as a library:
    import asyncio
    from async_utils import gather_limited

    async def main():
        results = await gather_limited(
            [fetch(url) for url in urls], limit=5
        )

    asyncio.run(main())

Run directly for a demo:
    python async_utils.py
"""

import asyncio
import time


async def gather_limited(coros, limit=5):
    """
    Run a list of coroutines concurrently, but never more than `limit`
    at once. Returns results in the same order as the input list.
    """
    semaphore = asyncio.Semaphore(limit)

    async def run_with_limit(coro):
        async with semaphore:
            return await coro

    return await asyncio.gather(*(run_with_limit(c) for c in coros))


async def with_timeout(coro, seconds):
    """
    Await a coroutine but cancel it and raise asyncio.TimeoutError if it
    doesn't finish within `seconds`. Thin, explicit wrapper around
    asyncio.wait_for for readability in calling code.
    """
    return await asyncio.wait_for(coro, timeout=seconds)


if __name__ == "__main__":
    async def fake_network_call(n, duration=0.5):
        await asyncio.sleep(duration)
        return f"result-{n}"

    async def main():
        print("Demo 1: 10 'network calls' with concurrency capped at 3\n")
        start = time.monotonic()
        coros = [fake_network_call(i) for i in range(10)]
        results = await gather_limited(coros, limit=3)
        elapsed = time.monotonic() - start
        print(f"Results: {results}")
        print(f"Elapsed: {elapsed:.2f}s "
              f"(unlimited concurrency would take ~0.5s, "
              f"fully sequential would take ~{0.5*10:.1f}s)\n")

        print("Demo 2: a coroutine that exceeds its timeout\n")
        try:
            await with_timeout(fake_network_call("slow", duration=2), seconds=0.5)
        except asyncio.TimeoutError:
            print("Caught expected asyncio.TimeoutError")

    asyncio.run(main())
