from brownie import interface
import time
from rich.console import Console
from helpers.constants import SUSHI_ROUTER, MaxUint256
from helpers.eth_registry import registry

console = Console()
tokens = registry.tokens
curve = registry.curve

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
        int(time.time()) + 120000000, # Add some time so tests don't fail,
        {"from": account, "value": amount}
    )

    console.print("[green]Test assets acquired![/green]")

def generate_curve_LP_assets(account, amount, sett_config):
    console.print("[yellow]Depositing for LP tokens...[/yellow]")


    poolInfo = sett_config.params.curvePool

    # ibBTC Vault Swap's function signature is differnet since it is actually a Zap
    if sett_config.params.want == tokens.ibbtcCrv:
        # Generate wbtc
        path = [tokens.weth, tokens.wbtc]
        generate_test_assets(account, path, amount)
        wbtc = interface.IERC20(tokens.wbtc)
        wbtcAmount = wbtc.balanceOf(account.address)

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
            int(time.time()) + 120000000, # Add some time so tests don't fail,
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

    elif (
        sett_config.params.want == tokens.mimCrv) or (
            sett_config.params.want == tokens.fraxCrv
        ):
        # Generate usdc
        path = [tokens.weth, tokens.usdc]
        generate_test_assets(account, path, amount)
        usdc = interface.IERC20(tokens.usdc)
        usdcAmount = usdc.balanceOf(account.address)

        zap = interface.ICurveZapIbBTC(curve.crvUSDZap) # Function has the same signature
        usdc.approve(zap.address, MaxUint256, {"from": account})

        amounts = [0] * poolInfo.numElements
        amounts[poolInfo.usdcPosition] = usdcAmount
        zap.add_liquidity(
            sett_config.params.want, # MIM or FRAX Crv pool
            amounts,
            0,
            account.address,
            {"from": account}
        )

    # Add liquidity for pool in matter through Curve Swap
    else:
        # Generate wbtc
        path = [tokens.weth, tokens.wbtc]
        generate_test_assets(account, path, amount)
        wbtc = interface.IERC20(tokens.wbtc)
        wbtcAmount = wbtc.balanceOf(account.address)

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