import asyncio
import time
import random

from loguru import logger
from web3 import AsyncWeb3
from eth_account import Account as EthereumAccount
from web3.exceptions import TransactionNotFound
from web3.middleware import async_geth_poa_middleware

from config import RPC
from settings import GAS_MULTIPLIER, GWEI
from eth_account.messages import encode_defunct, SignableMessage


class Account:
    def __init__(self, wallet_info, chain: str) -> None:
        self.account_id = wallet_info['id']
        self.private_key = wallet_info['private_key']
        self.chain = chain
        self.explorer = RPC[chain]["explorer"]
        self.token = RPC[chain]["token"]
        self.proxy = f"http://{wallet_info['proxy']}"

        request_kwargs = {}
        
        if self.proxy:
            request_kwargs = {"proxies": {"https": self.proxy, "http": self.proxy}}

        self.w3 = AsyncWeb3(
            AsyncWeb3.AsyncHTTPProvider(random.choice(RPC[chain]["rpc"])),
            middlewares=[async_geth_poa_middleware],
            request_kwargs=request_kwargs
        )
        self.account = EthereumAccount.from_key(self.private_key)
        self.address = self.account.address

    async def get_tx_data(self, value: int = 0):
        tx = {
            "chainId": await self.w3.eth.chain_id,
            "from": self.address,
            "value": value,
            "gasPrice": self.w3.to_wei(GWEI, 'gwei'),
            "nonce": await self.w3.eth.get_transaction_count(self.address),
        }
        return tx

    def get_contract(self, contract_address: str, abi):
        contract_address = self.w3.to_checksum_address(contract_address)

        contract = self.w3.eth.contract(address=contract_address, abi=abi)

        return contract

    async def wait_until_tx_finished(self, tx_hash: str, max_wait_time=300):
        start_time = time.time()
        while True:
            try:
                receipts = await self.w3.eth.get_transaction_receipt(tx_hash)
                status = receipts.get("status")
                if status == 1:
                    logger.success(f"[{self.account_id}][{self.address}] {self.explorer}{tx_hash} successfully!")
                    return True
                elif status is None:
                    await asyncio.sleep(0.3)
                else:
                    logger.error(f"[{self.account_id}][{self.address}] {self.explorer}{tx_hash} transaction failed!")
                    return False
            except TransactionNotFound:
                if time.time() - start_time > max_wait_time:
                    print(f'FAILED TX: {tx_hash}')
                    return False
                await asyncio.sleep(1)

    async def sign(self, transaction):
        gas = await self.w3.eth.estimate_gas(transaction)
        gas = int(gas * GAS_MULTIPLIER)

        transaction.update({"gas": gas})

        signed_txn = self.w3.eth.account.sign_transaction(transaction, self.private_key)

        return signed_txn

    async def send_raw_transaction(self, signed_txn):
        txn_hash = await self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)

        return txn_hash

    def sign_msg(self, encoded_msg: SignableMessage):
        return self.w3.eth.account.sign_message(encoded_msg, self.account.key)

    def get_signed_code(self, msg) -> str:
        return self.sign_msg(encode_defunct(text=msg)).signature.hex()
