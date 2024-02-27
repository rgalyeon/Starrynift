import asyncio
import random
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from itertools import count

import questionary
from loguru import logger
from questionary import Choice

from modules_settings import *
from utils.sleeping import sleep
from utils.logs_handler import filter_out_utils
from utils.password_handler import get_wallet_data
from settings import (
    RANDOM_WALLET,
    SLEEP_FROM,
    SLEEP_TO,
    QUANTITY_THREADS,
    THREAD_SLEEP_FROM,
    THREAD_SLEEP_TO,
    USE_LOGS
)
from config import placeholder


def get_module():
    counter = count(1)
    result = questionary.select(
        "Select a method to get started",
        choices=[
            Choice(f"{next(counter)}) Encrypt private keys and proxies", encrypt_privates),
            Choice(f"{next(counter)}) Make deposit from OKX", withdraw_okx),
            Choice(f"{next(counter)}) Farm starrynift", farm_starrynift),
            Choice(f"{next(counter)}) Use custom routes", custom_routes),
            Choice(f"{next(counter)}) Use automatic routes", automatic_routes),
            Choice(f"{next(counter)}) Exit", "exit"),
        ],
        qmark="⚙️ ",
        pointer="✅ "
    ).ask()
    if result == "exit":
        print("❤️ Project author – https://t.me/rgalyeon")
        print("❤️ Our Web3 and Trading community - https://t.me/tradium")
        print("❤️ Best Web3 course -  https://web3.cvizor.com\n")
        sys.exit()
    return result


def get_wallets():
    wallets_data = get_wallet_data()
    return list(wallets_data.values())


async def run_module(module, wallet_data):
    try:
        await module(wallet_data)
    except Exception as e:
        logger.error(e)
        import traceback

        traceback.print_exc()

    await sleep(SLEEP_FROM, SLEEP_TO)


def _async_run_module(module, wallet_data):
    asyncio.run(run_module(module, wallet_data))


def main(module):
    if module == encrypt_privates:
        return encrypt_privates(force=True)
    wallets_data = get_wallets()

    if RANDOM_WALLET:
        random.shuffle(wallets_data)

    with ThreadPoolExecutor(max_workers=QUANTITY_THREADS) as executor:
        for _, wallet_data in enumerate(wallets_data, start=1):
            executor.submit(
                _async_run_module,
                module,
                wallet_data
            )

            sleep_time = random.randint(THREAD_SLEEP_FROM, THREAD_SLEEP_TO)
            time.sleep(sleep_time)


if __name__ == '__main__':
    print(placeholder)
    print("❤️ Project author – https://t.me/rgalyeon")
    print("❤️ Our Web3 and Trading community - https://t.me/tradium")
    print("❤️ Best Web3 course -  https://web3.cvizor.com\n")

    if USE_LOGS:
        logger.add('logs.txt', filter=filter_out_utils)

    module = get_module()
    main(module)

    logger.success('Script is finished 🚀')
