import pytest
from brownie import (
    accounts,
    interface,
)
from rich.console import Console
from badger_utils.coingecko_utils import fetch_usd_value

console = Console()

# Prices at 11/24/2021 5PM
# Change for dynamic fetching once the CG utils support them
cvx_usd = 24.05
crv_usd = 5.72

STRAT_KEYS = [
    "native.renCrv",
    "native.sbtcCrv",
    "native.tbtcCrv",
    "native.hbtcCrv",
    "native.pbtcCrv",
    "native.obtcCrv",
    "native.bbtcCrv",
    "native.tricrypto2",
]

# Addresses of strategies to check for rewards on baseRewardsPool
OLD_STRATEGIES = {
    "native.renCrv": "0x6582a5b139fc1c6360846efdc4440d51aad4df7b",
    "native.sbtcCrv": "0xf1ded284e891943b3e9c657d7fc376b86164ffc2",
    "native.tbtcCrv": "0x522bb024c339a12be1a47229546f288c40b62d29",
    "native.hbtcCrv": "0xff26f400e57bf726822eacbb64fa1c52f1f27988",
    "native.pbtcCrv": "0x1C1fD689103bbFD701b3B7D41A3807F12814033D",
    "native.obtcCrv": "0x2bb864cdb4856ab2d148c5ca52dd7ccec126d138",
    "native.bbtcCrv": "0x4f3e7a4566320b2709fd1986f2e9f84053d3e2a0",
    "native.tricrypto2": "0x2eB6479c2f033360C0F4575A88e3b8909Cbc6a03",
}

def main():

    cvx = interface.IERC20("0x4e3fbd56cd56c3e72c1403e103b45db9da5b9d2b")
    cvxCrv = interface.IERC20("0x62b9c7356a2dc64a1969e19c23e4f579f9810aa7")
    crv = interface.IERC20("0xd533a949740bb3306d119cc777fa900ba034cd52")

    total_cvx = 0
    total_cvxCrv = 0
    total_crv = 0

    for strategy_key in STRAT_KEYS:
        console.print(f"\n[yellow]Rewards to claim from {strategy_key}:[/yellow]")

        # Get current strategy
        strategy = interface.IStrategyConvexStakingOptimizer(OLD_STRATEGIES[strategy_key])
        strat_actor = accounts.at(OLD_STRATEGIES[strategy_key], force=True)

        # Get reward pool
        baseRewardsPool = interface.IBaseRewardsPool(strategy.baseRewardsPool())

        # Call getRewards on baseRewardsPool
        baseRewardsPool.getReward(strat_actor.address, True, {"from": strat_actor})

        cvx_balance = cvx.balanceOf(strategy)
        cvxCrv_balance = cvxCrv.balanceOf(strategy)
        crv_balance = crv.balanceOf(strategy)

        console.print(f"\nCVX to recover: {cvx_balance/1e18} - ${cvx_usd * (cvx_balance/1e18)} USD")
        console.print(f"cvxCrv to recover: {cvxCrv_balance/1e18} - ${crv_usd * (cvxCrv_balance/1e18)} USD")
        console.print(f"crv to recover: {crv_balance/1e18} - ${crv_usd * (crv_balance/1e18)} USD")

        total_cvx = total_cvx + cvx_balance
        total_cvxCrv = total_cvxCrv + cvxCrv_balance
        total_crv = total_crv + crv_balance

    console.print("\n\n---------------------------------------------------")
    console.print(f"Total CVX to recover: {total_cvx/1e18} - ${cvx_usd * (total_cvx/1e18)} USD")
    console.print(f"Total cvxCrv to recover: {total_cvxCrv/1e18} - ${crv_usd * (total_cvxCrv/1e18)} USD")
    console.print(f"Total crv to recover: {total_crv/1e18} - ${crv_usd * (total_crv/1e18)} USD")



