from modules import *


async def withdraw_okx(wallet_info):
    """
    Withdraw ETH from OKX
    ______________________________________________________
    min_amount - min amount of token
    max_amount - max_amount of token
    chains - ['bsc']
    terminate - If True - terminate program if money is not withdrawn
    skip_enabled - If True, the skip_threshold check will be applied; otherwise, it will be ignored
    skip_threshold - If skip_enabled is True and the wallet balance is greater than or equal to this threshold,
                     skip the withdrawal

    """
    token = 'BNB'
    chains = ['bsc']

    min_amount = 0.00327
    max_amount = 0.00650

    terminate = True

    skip_enabled = True
    skip_threshold = 0.00327
    okx_exchange = Okx(wallet_info, chains)
    await okx_exchange.okx_withdraw(min_amount, max_amount, token, terminate, skip_enabled, skip_threshold)


async def farm_starrynift(wallet_info):
    """
    Module mint a pass if it is not on the account and performs daily tasks.
    The module also checks how much time is left before you can perform a daily task and if you run the module
    before the time, the software will wait until the task becomes available.

    Parameters
    ----------
    sleep_from - minimum sleep delay after pass minting
    sleep_to - maximum sleep delay after pass minting
    """
    sleep_after_mint_pass_from = 100
    sleep_after_mint_pass_to = 300

    starry = StarryNift(wallet_info, 'bsc')
    await starry.farm_starry(sleep_after_mint_pass_from, sleep_after_mint_pass_to)


async def custom_routes(wallet_info):
    """
    ______________________________________________________
    Disclaimer - You can add modules to [] to select random ones,
    example [module_1, module_2, [module_3, module_4], module 5]
    The script will start with module 1, 2, 5 and select a random one from module 3 and 4

    You can also specify None in [], and if None is selected by random, this module will be skipped

    You can also specify () to perform the desired action a certain number of times
    example (send_mail, 1, 10) run this module 1 to 10 times
    """

    use_modules = [withdraw_okx, automatic_routes]

    sleep_from = 140
    sleep_to = 300

    random_module = False

    routes = Routes(wallet_info)
    await routes.start(use_modules, sleep_from, sleep_to, random_module)


async def automatic_routes(wallet_info):
    """
    The module automatically generates paths that a wallet will take, changing the probabilities of choosing
    a particular module for each wallet.

    Parameters
    ----------
    transaction_count - number of transactions
    cheap_ratio - from 0 to 1, the ratio of cheap transactions in the route construction (1.0 - modules only from
                  the cheap_modules list will be used, 0 - modules from the expensive_modules list will be used,
                  0.5 - the probability of choosing a cheap module or an expensive one = 50%)
    cheap_modules - list of modules to be used as cheap ones
    expensive_modules - list of modules to be used as expensive ones
    sleep_from - minimum sleep delay between module (transaction) executions
    sleep_to - maximum sleep delay between module executions
    use_none - if True, the software will occasionally skip module execution with some probability
    ----------
    """

    transaction_count = 200
    cheap_ratio = 1.0

    sleep_from = 84000
    sleep_to = 89000

    use_none = False
    cheap_modules = [farm_starrynift]
    expensive_modules = []

    routes = Routes(wallet_info)
    await routes.start_automatic(transaction_count, cheap_ratio,
                                 sleep_from, sleep_to,
                                 cheap_modules, expensive_modules,
                                 use_none)
