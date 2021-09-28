import brownie
from brownie import *
from helpers.constants import MaxUint256
from helpers.SnapshotManager import SnapshotManager
from config import DEFAULT_WITHDRAWAL_FEE
from helpers.time import days

MAX_BASIS = 10000


def test_is_profitable(deployed):
    deployer = deployed.deployer
    vault = deployed.vault
    controller = deployed.controller
    strategy = deployed.strategy
    want = deployed.want
    randomUser = accounts[6]

    initial_balance = want.balanceOf(deployer)

    settKeeper = accounts.at(vault.keeper(), force=True)

    snap = SnapshotManager(vault, strategy, controller, "StrategySnapshot")

    # Deposit
    assert want.balanceOf(deployer) > 0

    depositAmount = int(want.balanceOf(deployer) * 0.8)
    assert depositAmount > 0

    want.approve(vault.address, MaxUint256, {"from": deployer})

    snap.settDeposit(depositAmount, {"from": deployer})

    # Earn
    with brownie.reverts("onlyAuthorizedActors"):
        vault.earn({"from": randomUser})

    min = vault.min()
    max = vault.max()
    remain = max - min

    snap.settEarn({"from": settKeeper})

    snap.settTend({"from": settKeeper})

    chain.sleep(days(50))
    chain.mine(10)

    snap.settTend({"from": settKeeper})

    snap.settHarvest({"from": deployer})
    
    snap.settWithdrawAll({"from": deployer})

    ending_balance = want.balanceOf(deployer)

    initial_balance_with_fees = initial_balance * (
        1 - (DEFAULT_WITHDRAWAL_FEE / MAX_BASIS)
    )

    print("Initial Balance")
    print(initial_balance)
    print("initial_balance_with_fees")
    print(initial_balance_with_fees)
    print("Ending Balance")
    print(ending_balance)

    assert ending_balance > initial_balance_with_fees
    assert false