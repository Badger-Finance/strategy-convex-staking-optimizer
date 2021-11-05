import time
from brownie import accounts, network, SettV3, BadgerRegistry, StrategyConvexStakingOptimizer
from config import REGISTRY
from helpers.constants import AddressZero
from helpers.utils import get_config
import click
from rich.console import Console

console = Console()

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

STRATEGIES = {
    "native.renCrv": "0x61e16b46F74aEd8f9c2Ec6CB2dCb2258Bdfc7071",
    "native.sbtcCrv": "0xCce0D2d1Eb2310F7e67e128bcFE3CE870A3D3a3d",
    "native.tbtcCrv": "0xAB73Ec65a1Ef5a2e5b56D5d6F36Bee4B2A1D3FFb",
    "native.hbtcCrv": "0x8c26D9B6B80684CC642ED9eb1Ac1729Af3E819eE",
    "native.pbtcCrv": "0xA9A646668Df5Cec5344941646F5c6b269551e53D",
    "native.obtcCrv": "0x5dd69c6D81f0a403c03b99C5a44Ef2D49b66d388",
    "native.bbtcCrv": "0xF2F3AB09E2D8986fBECbBa59aE838a5418a6680c",
    "native.tricrypto2": "0x647eeb5C5ED5A71621183f09F6CE8fa66b96827d",
}

def main():
    """
    TO BE RUN BEFORE PROMOTING TO PROD

    Checks and Sets all Keys for Vault and Strategy Against the Registry

    1. Checks all Keys
    """

    for key in STRAT_KEYS:

        strategy = StrategyConvexStakingOptimizer.at(STRATEGIES[key])

        assert strategy.paused() == False

        console.print("[blue]Strategy: [/blue]", key)
        console.print("Strategy:", strategy.address)
        console.print("Want:", strategy.want())

        # Get production addresses from registry
        registry = BadgerRegistry.at(REGISTRY)

        governance = registry.get("governance")
        devGovernance = registry.get("devGovernance")
        guardian = registry.get("guardian")
        keeper = registry.get("keeper")
        controller = registry.get("controller")
        badgerTree = registry.get("badgerTree")

        assert governance != AddressZero
        assert guardian != AddressZero
        assert keeper != AddressZero
        assert controller != AddressZero
        assert badgerTree != AddressZero

        # Confirm all productions parameters
        check_parameters(
            strategy, 
            governance,
            devGovernance, 
            guardian, 
            keeper, 
            controller, 
            badgerTree, 
            key
        )


def check_parameters(
    strategy, 
    governance,
    devGovernance, 
    guardian, 
    keeper, 
    controller, 
    badgerTree, 
    key
):
    config = get_config(key)

    assert strategy.want() == config.params.want
    assert strategy.controller() == controller

    assert strategy.performanceFeeGovernance() == 2000
    assert strategy.performanceFeeStrategist() == 0
    assert strategy.withdrawalFee() == 10
    assert strategy.autoCompoundingPerformanceFeeGovernance() == 0
    assert strategy.autoCompoundingBps() == 2000

    assert strategy.keeper() == keeper
    assert strategy.guardian() == guardian
    assert strategy.strategist() == devGovernance
    assert strategy.governance() == governance

    assert strategy.pid() == config.params.pid
    assert strategy.cvxHelperVault() == config.params.cvxHelperVault
    assert strategy.cvxCrvHelperVault() == config.params.cvxCrvHelperVault
    assert strategy.curvePool() == (
        (  
            config.params.curvePool.swap, 
            config.params.curvePool.wbtcPosition, 
            config.params.curvePool.numElements
        )
    )




    # Not all strategies use the badgerTree
    try:
        if strategy.badgerTree() != AddressZero:
            assert strategy.badgerTree() == badgerTree
    except:
        pass

    console.print("[green]All Parameters checked![/green]")


def connect_account():
    click.echo(f"You are using the '{network.show_active()}' network")
    dev = accounts.load(click.prompt("Account", type=click.Choice(accounts.load())))
    click.echo(f"You are using: 'dev' [{dev.address}]")
    return dev
