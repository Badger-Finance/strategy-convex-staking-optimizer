from brownie import interface
import time
from rich.console import Console
from helpers.constants import SUSHI_ROUTER

console = Console()

def generate_test_assets(account, path, amount):
    console.print("[yellow]Swapping for test assets...[/yellow]")
    # Using Sushiswap router
    router = interface.IUniswapRouterV2(SUSHI_ROUTER)

    for address in path:
        asset = interface.IERC20(address)
        asset.approve(router.address, 999999999999999999999999999999, {"from": account})

    # Buy path[n-1] token with "amount" of path[0] token
    router.swapExactETHForTokens(
        0,
        path,
        account,
        int(time.time()) + 1200, # Now + 20mins,
        {"from": account, "value": amount}
    )

    console.print("[green]Test assets acquired![/green]")

# def generate_curve_LP_assets(account, asset, amount):

