import time
from brownie import accounts, network, SettV3, BadgerRegistry, StrategyConvexStakingOptimizer
from config import REGISTRY
from helpers.constants import AddressZero
from helpers.utils import get_config
import click
import json
from rich.console import Console
from config.badger_config import badger_config

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
    "native.ibbtcCrv",
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
    "native.ibbtcCrv": "0x6D4BA00Fd7BB73b5aa5b3D6180c6f1B0c89f70D1",
}

def main():
    """
    TO BE RUN BEFORE PROMOTING TO PROD

    Checks the parameters of all of the strategies listed above.
    """

    for key in STRAT_KEYS:

        strategy = StrategyConvexStakingOptimizer.at(STRATEGIES[key])

        assert strategy.paused() == False

        console.print(f"[blue]Checking {key}[/blue]")
        console.print("Strategy:", strategy.address)
        console.print("Want:", strategy.want())

        # Get production addresses from registry
        registry = BadgerRegistry.at(REGISTRY)

        governance = registry.get("governance")
        devGovernance = registry.get("devGovernance")
        guardian = registry.get("guardian")
        keeper = registry.get("keeper")
        badgerTree = registry.get("badgerTree")

        with open(badger_config.prod_json) as f:
            deploy = json.load(f)

        # Controllers are different for different strategies
        if key in ["native.renCrv", "native.sbtcCrv", "native.tbtcCrv"]:
            controller = deploy["sett_system"]["controllers"]["native"]
        elif key in ["native.ibbtcCrv"]:
            controller = "0xe505F7C2FFcce7Ae4b076456BC02A70D8fe8d4d2"
        else:
            controller = deploy["sett_system"]["controllers"]["experimental"]

        assert governance != AddressZero
        assert guardian != AddressZero
        assert keeper != AddressZero
        assert badgerTree != AddressZero
        assert controller != AddressZero

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
    assert strategy.stableSwapSlippageTolerance() == 500
    assert strategy.minThreeCrvHarvest() == 1000e18

    assert strategy.keeper() == keeper
    assert strategy.guardian() == guardian
    assert strategy.strategist() == devGovernance
    assert strategy.governance() == governance

    assert strategy.pid() == config.params.pid
    assert strategy.cvxCrvHelperVault() == config.params.cvxCrvHelperVault
    assert strategy.badgerTree() == badgerTree

    console.print("[green]All Parameters checked![/green]")