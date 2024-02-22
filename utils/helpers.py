from loguru import logger
from settings import RETRY_COUNT
from utils.sleeping import sleep
import traceback
from main import transaction_lock


def retry(func):
    async def wrapper(*args, **kwargs):
        retries = 0
        while retries <= RETRY_COUNT:
            try:
                with transaction_lock:
                    result = await func(*args, **kwargs)
                    await sleep(5, 10)
                return result
            except Exception as e:
                logger.error(f"Error | {e}")
                traceback.print_exc()
                await sleep(10, 20)
                retries += 1

    return wrapper
