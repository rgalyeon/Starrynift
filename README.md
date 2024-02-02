![Imgur](https://i.imgur.com/gRXuyiY.png)
# Starrynift
Software for working with the Starrynift project. Supports multiple OKX accounts, multithreading, encrypts sensitive data, after encryption wallets can be started using only the wallet address (no need to re-enter data).

## Description
With the help of the software you can make a withdrawal BNB from the OKX exchange, register an account with a referral link, mint pass, and perform daily tasks.

**Modules**
1. `encrypt_privates_and_proxy` - module is necessary for the first launch of the software. Reads data from the table `wallet_data.xlsx`, encrypts and deletes sensitive data from the table. For repeated runs it is enough to specify only the wallet address, because the rest of the data is stored in encrypted form. If you want to add new data (add wallets or change proxies), you will need to use this module again.
2. `withdraw_okx` - module for withdrawing tokens from the OKX. Supports checking the balance on the wallet to avoid withdrawing money in case it is already in the chain
3. `farm_starrynift` - mint pass if it wasn't on the account and performs a daily task.
4. `custom_routes` - module for customizing your own route. Use cases: [withdraw_okx, farm_starrynift] for first entry project, or [withdraw_okx, automatic_routes] to run the script for many days ahead.
5. `automatic_routes` - module for automatic route building. You can customize the number of required transactions, you can add skipping some transactions (if you want to skip some day). You can configure delays between transactions. You can control the probability of making cheap transactions and expensive ones (this feature is not needed in this project).

## Installation
```bash
git clone https://github.com/rgalyeon/Starrynift.git
cd Starrynift
python -m venv venv
source venv/bin/activate (on MacOs) or .\venv\Scripts\activate (on Windows)
pip install -r requirements.txt
```

## How to run software
### 1. First, you must fill in the appropriate columns in the `wallet_data.xslx` table:
- `address` - wallet address
- `private` - private key 
- `proxy` - proxy, if used for wallet in the format `login:pass@ip:port`
- `okx_api` - api okx account in the format `api;secret;password` (you can customize okx api for each wallet)
- `ref_link` - referral link for Starrynift (you can customize referral link for each wallet)

### 2. Encrypt data
- Run script with `python main.py` command and choose `Encrypt private keys and proxies`
- Set up a password to access the data

#### 3. Customize the modules and get them up and running. 
- Set up general settings in `settings.py` (thread_count, retry_count, etc...)
- Set up modules settings in `module_settings.py`
- Add the wallet addresses you want to run to the `wallet_data.xlsx` file (only wallet addresses are needed after encryption)
- Run script with `python main.py` command and choose necessary module.

## Contacts
- [Author](https://t.me/rgalyeon) | [Tradium Community](https://t.me/tradium)
- Buy me a coffee: `rgalyeon.eth`
