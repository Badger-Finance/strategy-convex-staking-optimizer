from brownie import interface
import time
from rich.console import Console
from helpers.constants import SUSHI_ROUTER, MaxUint256
from helpers.eth_registry import registry

console = Console()
tokens = registry.tokens

def generate_test_assets(account, path, amount):
    console.print("[yellow]Swapping for test assets...[/yellow]")
    # Using Sushiswap router
    router = interface.IUniswapRouterV2(SUSHI_ROUTER)

    for address in path:
        asset = interface.IERC20(address)
        asset.approve(router.address, MaxUint256, {"from": account})

    # Buy path[n-1] token with "amount" of path[0] token
    router.swapExactETHForTokens(
        0,
        path,
        account,
        int(time.time()) + 1200, # Now + 20mins,
        {"from": account, "value": amount}
    )

    console.print("[green]Test assets acquired![/green]")

def generate_curve_LP_assets(account, amount, sett_config):
    console.print("[yellow]Depositing for LP tokens...[/yellow]")
    # Generate wbtc
    path = [tokens.weth, tokens.wbtc]
    generate_test_assets(account, path, amount)
    wbtc = interface.IERC20(tokens.wbtc)
    wbtcAmount = wbtc.balanceOf(account.address)

    poolInfo = sett_config.params.curvePool

    # ibBTC Vault Swap's function signature is differnet since it is actually a Zap
    if sett_config.params.want == tokens.ibbtcCrv:
        # Swap wBTC for ibBTC through Sushiswap
        router = interface.IUniswapRouterV2(SUSHI_ROUTER)
        path = [tokens.wbtc, tokens.ibbtc]
        for address in path:
            asset = interface.IERC20(address)
            asset.approve(router.address, MaxUint256, {"from": account})

        router.swapExactTokensForTokens(
            wbtcAmount,
            0,
            path,
            account,
            int(time.time()) + 1200, # Now + 20mins,
            {"from": account}
        )

        zap = interface.ICurveZapIbBTC(poolInfo.swap)
        ibBTC = interface.IERC20(tokens.ibbtc)
        ibBTC.approve(zap.address, MaxUint256, {"from": account})

        amounts = [0] * poolInfo.numElements
        amounts[poolInfo.ibbtcPosition] = ibBTC.balanceOf(account.address)
        zap.add_liquidity(
            sett_config.params.want, # ibBTC/sBTC Pool
            amounts,
            0,
            account.address,
            {"from": account}
        )

    # Add liquidity for pool in matter through Curve Swap
    else:
        swap = interface.ICurveFi(poolInfo.swap)
        wbtc.approve(poolInfo.swap, MaxUint256, {"from": account})
        amounts = [0] * poolInfo.numElements
        amounts[poolInfo.wbtcPosition] = wbtcAmount
        swap.add_liquidity[f'uint[{poolInfo.numElements}],uint'](
            amounts,
            0,
            {"from": account}
        )

    console.print("[green]Test LP tokens acquired![/green]")