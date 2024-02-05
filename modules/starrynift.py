import random

from .account import Account
import aiohttp
from fake_useragent import UserAgent
from config import PASS_CONTRACT, PASS_ABI, DAILY_CONTRACT, DAILY_ABI
from loguru import logger
from utils.sleeping import sleep
from utils.helpers import retry
from datetime import timedelta


class StarryNift(Account):
    def __init__(self, wallet_info, chain: str):
        super().__init__(wallet_info=wallet_info, chain=chain)

        headers = {
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
            "Authorization": "Bearer null",
            "Connection": "keep-alive",
            "Content-Type": "application/json;charset=UTF-8",
            "Host": "api.starrynift.art",
            "Origin": "https://starrynift.art",
            "Referer": "https://starrynift.art/",
            "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": UserAgent(os='windows').random,
        }

        referral_link = wallet_info['ref_link']
        self.referral_code = referral_link.split('=')[1] if referral_link else ''
        self.session = aiohttp.ClientSession(headers=headers, trust_env=True)
        self.pass_contract = self.get_contract(PASS_CONTRACT, PASS_ABI)
        self.daily_contact = self.get_contract(DAILY_CONTRACT, DAILY_ABI)

    async def get_signature(self):
        url = f"https://api.starrynift.art/api-v2/starryverse/auth/wallet/challenge?address={self.address}"

        resp = await self.session.get(url=url, proxy=self.proxy)
        return (await resp.json()).get('message')

    async def login(self):
        logger.info(f'[{self.account_id}][{self.address}] Start login')
        signature = self.get_signed_code(await self.get_signature())

        json_data = {
            "address": self.address,
            "signature": signature,
            "referralCode": self.referral_code,
            "referralSource": 0
        }

        resp = await self.session.post(url='https://api.starrynift.art/api-v2/starryverse/auth/wallet/evm/login',
                                       json=json_data, proxy=self.proxy)

        auth_token = (await resp.json()).get("token")
        if auth_token:
            self.session.headers["Authorization"] = f"Bearer {auth_token}"

        return bool(auth_token)

    async def check_minted_pass(self):
        return await self.pass_contract.functions.balanceOf(self.address).call()

    async def mint_pass(self):
        logger.info(f'[{self.account_id}][{self.address}] Start mint pass')
        signature = await self.get_mint_signature()

        data = f"0xf75e0384" \
               f"0000000000000000000000000000000000000000000000000000000000000020" \
               f"000000000000000000000000{self.address[2:].lower()}" \
               f"0000000000000000000000000000000000000000000000000000000000000001" \
               f"0000000000000000000000000000000000000000000000000000000000000060" \
               f"0000000000000000000000000000000000000000000000000000000000000041" \
               f"{signature[2:]}" \
               f"00000000000000000000000000000000000000000000000000000000000000"

        tx_data = await self.get_tx_data(0)
        tx_data['to'] = "0xC92Df682A8DC28717C92D7B5832376e6aC15a90D"
        tx_data['data'] = data
        # tx_data['gas'] = 250000

        sgn_tx = await self.sign(tx_data)
        tx_hash = await self.send_raw_transaction(sgn_tx)

        if await self.wait_until_tx_finished(tx_hash.hex()) and await self.send_mint_hash(tx_hash.hex()):
            logger.success(f'[{self.account_id}][{self.address}] Successfully mint pass')

    async def get_mint_signature(self):
        json_data = {
            "category": 1
        }

        resp = await self.session.post('https://api.starrynift.art/api-v2/citizenship/citizenship-card/sign',
                                       json=json_data, proxy=self.proxy)
        return (await resp.json()).get('signature')

    async def send_mint_hash(self, tx_hash):
        json_data = {
            'txHash': tx_hash
        }

        resp = await self.session.post('https://api.starrynift.art/api-v2/webhook/confirm/citizenship/mint',
                                       json=json_data, proxy=self.proxy)
        return (await resp.json()).get('ok') == 1

    async def daily_claim(self):
        logger.info(f'[{self.account_id}][{self.address}] Start claim points')
        tx_data = await self.get_tx_data(0)

        tx_data['to'] = DAILY_CONTRACT
        tx_data['data'] = "0x9e4cda43"
        # gas_limit = 90000

        sgn_tx = await self.sign(tx_data)
        tx_hash = await self.send_raw_transaction(sgn_tx)

        if await self.wait_until_tx_finished(tx_hash.hex()) and await self.send_daily_hash(tx_hash.hex()):
            logger.success(f'[{self.account_id}][{self.address}] Successfully claimed points')

    async def send_daily_hash(self, tx_hash):
        json_data = {
            "txHash": tx_hash
        }

        resp = await self.session.post('https://api.starrynift.art/api-v2/webhook/confirm/daily-checkin/checkin',
                                       json=json_data, proxy=self.proxy)
        return (await resp.json()).get('ok') == 1

    async def get_daily_claim_time(self):
        return await self.daily_contact.functions.getTimeUntilNextSignIn(self.address).call()

    async def logout(self):
        await self.session.close()

    @retry
    async def farm_starry(self, sleep_after_mint_from, sleep_after_mint_to):
        if await self.login():
            logger.success(f'[{self.account_id}][{self.address}] Successfully logged in')
            await sleep(10, 20)
            if not await self.check_minted_pass():
                await self.mint_pass()
                await sleep(sleep_after_mint_from, sleep_after_mint_to)

            time_to_claim = await self.get_daily_claim_time()
            while time_to_claim:
                logger.warning(
                    f"[{self.account_id}][{self.address}] Next claim will be available after {str(timedelta(seconds=time_to_claim))}")
                await sleep(time_to_claim, time_to_claim + random.randint(100, 500))
                time_to_claim = await self.get_daily_claim_time()
            if time_to_claim == 0:
                await self.daily_claim()
        await self.logout()
