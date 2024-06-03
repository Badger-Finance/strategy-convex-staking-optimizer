from helpers.SnapshotManager import SnapshotManager
from brownie import (
    StrategyConvexStakingOptimizer,
    Controller,
    SettV4,
    accounts,
    interface,
)
from rich.console import Console

console = Console()

"""
Allows to simulate any of Harvest, Earn or Tend on a live instance of a Sett
Use the following to run:

brownie run scripts/tests/simulate_sett_actions.py main strategy_address action

Where action can be: harvest, earn or tend.

It defaults to simulating a harvest on the wiBTC/sBTC-f Sett
"""


def main(strategyAddress="0x6D4BA00Fd7BB73b5aa5b3D6180c6f1B0c89f70D1", action="harvest"):
    strategy = StrategyConvexStakingOptimizer.at(strategyAddress)
    want = interface.IERC20(strategy.want())
    controller = Controller.at(strategy.controller())
    vault = SettV4.at(controller.vaults(want.address))

    strat_keeper = accounts.at(strategy.keeper(), force=True)
    vault_keeper = accounts.at(vault.keeper(), force=True)

    snap = SnapshotManager(vault, strategy, controller, "StrategySnapshot")

    if action == "harvest":
        snap.settHarvest({"from": strat_keeper})
    elif action == "earn":
        snap.settEarn({"from": vault_keeper})
    elif action == "tend":
        snap.settTend({"from": strat_keeper})
    else:
        console.print("[red]Action not recognized[/red]")