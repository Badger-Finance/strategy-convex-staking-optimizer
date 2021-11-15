import brownie
import pytest
import json
from brownie import (
    Controller,
    accounts,
    interface,
    chain,
    Wei,
    SettV4
)
from config.badger_config import badger_config
from rich.console import Console
from helpers.SnapshotManager import SnapshotManager
from helpers.utils import get_config
from helpers.constants import MaxUint256
from helpers.time import days
import time
from helpers.test.test_utils import generate_curve_LP_assets


##### Variables to tweak ######

harvest_time_after_deposit = days(3)
asset_deposit_amount = "1 ether"

###############################


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


@pytest.fixture()
def badger_deploy():
    with open(badger_config.prod_json) as f:
        return json.load(f)


@pytest.fixture()
def deployer(badger_deploy):
    return accounts.at(badger_deploy["deployer"], force=True)


@pytest.fixture()
def guardian(badger_deploy):
    return accounts.at(badger_deploy["guardian"], force=True)


@pytest.fixture()
def keeper():
    return accounts.at("0x711A339c002386f9db409cA55b6A35a604aB6cF6", force=True)


@pytest.fixture()
def governance_multi(badger_deploy):
    return accounts.at(badger_deploy["devMultisig"], force=True)


@pytest.fixture()
def timelock(badger_deploy):
    return accounts.at(badger_deploy["timelock"], force=True)


@pytest.fixture()
def bcvxCrv():
    return SettV4.at("0x2B5455aac8d64C14786c3a29858E43b5945819C0")


@pytest.fixture()
def bCvx():
    return SettV4.at("0x53c8e199eb2cb7c01543c137078a038937a68e40")  


@pytest.fixture()
def strategies(badger_deploy):
    return badger_deploy["sett_system"]["strategies"]


@pytest.fixture()
def test_vaults():
    return {
            "native.renCrv": "0xD3eC271d07f2f9a4eB5dfD314f84f8a94ba96145",
            "native.sbtcCrv": "0x8D7A5Bacbc763b8bA7c2BB983089b01bBF3C9408",
            "native.tbtcCrv": "0xe71246810751dfaf8430dcd838a1e58A904a2725",
            "native.hbtcCrv": "0x8E8Fd0dD9F8C69E621054538Fb106Ae77B0847DD",
            "native.pbtcCrv": "0xdD954ff59A99352aCF16AAd0801350a0742359E3",
            "native.obtcCrv": "0x0eC330A6f4e93204B9AA62a4e7A0C78D7849821E",
            "native.bbtcCrv": "0x68e8efd42A22BF4B53ecE7162d9aCbA2Ad2f9991",
            "native.tricrypto2": "0x29001E42899308A61d981c5f5780e4E4D727a0BB",
        }

@pytest.fixture(autouse=True)
def isolation(fn_isolation):
    pass


@pytest.mark.parametrize(
    "strategy_key",
    STRAT_KEYS,
)
def test_migrate_staking_optimizer(
    strategy_key,
    test_vaults,
    keeper,
    governance_multi,
    bcvxCrv,
    bCvx,
    deployer,
):

    console.print(f"[yellow]Processing {strategy_key}...[/yellow]")

    # Get current strategy
    strategy = interface.IStrategyConvexStakingOptimizer(OLD_STRATEGIES[strategy_key])
    # Get vault
    vault = interface.ISettV4(test_vaults[strategy_key])
    # Get want
    want = interface.IERC20(strategy.want())

    vault_governance = accounts.at(vault.governance(), force=True)

    # We must deploy new controller
    test_controller = Controller.deploy({"from": vault_governance})
    test_controller.initialize(
        deployer.address, 
        deployer.address, 
        keeper.address, 
        governance_multi.address,
        {"from": vault_governance}
    )

    # Get reward pools
    baseRewardsPool = interface.IBaseRewardsPool(strategy.baseRewardsPool())
    cvxCrvRewardsPool = interface.IBaseRewardsPool(strategy.cvxCrvRewardsPool())
    cvxRewardsPool = interface.IBaseRewardsPool(strategy.cvxRewardsPool())

    badgerTree = strategy.badgerTree()

    console.print(f"[blue]Old Strategy: [/blue]{strategy.address}")
    console.print(f"[blue]Vault: [/blue]{vault.address}")
    console.print(f"[blue]Want: [/blue]{want.address}")
    console.print("baseRewardsPool earned:", baseRewardsPool.earned(strategy.address))
    console.print("cvxCrvRewardsPool earned:", cvxCrvRewardsPool.earned(strategy.address))
    console.print("cvxRewardsPool earned:", cvxRewardsPool.earned(strategy.address))
    console.print("cvxCrvRewardsPool balanceOf:", cvxCrvRewardsPool.balanceOf(strategy.address))
    console.print("cvxRewardsPool balanceOf:", cvxRewardsPool.balanceOf(strategy.address))
    console.print("strategy.balanceOf():", strategy.balanceOf())

    # Harvest should revert due to lack of rewards on cvx and cvxCrv reward pools
    with brownie.reverts("RewardPool : Cannot withdraw 0"):
        strategy.harvest({"from": keeper})

    # Sets test controller on strat and vault
    strategy.setController(test_controller.address, {"from": governance_multi})
    assert strategy.controller() == test_controller.address
    vault.setController(test_controller.address, {"from": vault_governance})

    # Wires up strat and vualt to test controller
    test_gov = accounts.at(test_controller.governance(), force=True)
    test_strategist = accounts.at(test_controller.strategist(), force=True)
    wire_up_strategy(strategy, test_controller, test_gov, test_strategist)

    test_controller.setVault(want.address, vault.address, {"from": test_gov})
    assert test_controller.vaults(want.address) == vault

    # Set auto compounding Bps to 1 on strategy
    strategy.setAutoCompoundingBps(1, {"from": governance_multi})
    assert strategy.autoCompoundingBps() == 1

    # Deposit assets to vault and call earn
    config = get_config(strategy_key)
    randomUser = accounts[0]
    generate_curve_LP_assets(randomUser, Wei(asset_deposit_amount), config)

    user_balance = want.balanceOf(randomUser)

    assert user_balance > 0

    want.approve(vault.address, user_balance, {'from': randomUser})
    vault.depositAll({'from': randomUser})

    chain.sleep(60)
    chain.mine()

    vault.earn({"from": vault_governance})

    chain.sleep(harvest_time_after_deposit)
    chain.mine()

    console.print("cvxCrvRewardsPool balanceOf:", cvxCrvRewardsPool.balanceOf(strategy.address))
    console.print("cvxRewardsPool balanceOf:", cvxRewardsPool.balanceOf(strategy.address))

    # assert cvxCrvRewardsPool.earned(strategy.address) > 0
    # assert cvxRewardsPool.earned(strategy.address) > 0 

    tree_bcvx_before = bCvx.balanceOf(badgerTree)
    tree_bcvxCrv_before = bcvxCrv.balanceOf(badgerTree)
    postion_before = strategy.balanceOf()

    strategy.harvest({"from": keeper})

    tree_bcvx_after = bCvx.balanceOf(badgerTree)
    tree_bcvxCrv_after = bcvxCrv.balanceOf(badgerTree)
    postion_after = strategy.balanceOf()

    console.print("\nHarvest Balances Diff")
    console.print("\nTree bcvx:", tree_bcvx_after-tree_bcvx_before)
    console.print("\nTree bcvxCrv:", tree_bcvxCrv_after-tree_bcvxCrv_before)
    console.print("\nStrat Position:", postion_after-postion_before)


def wire_up_strategy(strategy, controller, governance, test_strategist):
    console.print(f"[blue]Migrating strategy[/blue]")
    # Approve new strategy for want on Controller
    controller.approveStrategy(
        strategy.want(), strategy.address, {"from": governance}
    )
    assert controller.approvedStrategies(strategy.want(), strategy.address)

    # Set new strategy for want on Controller
    controller.setStrategy(strategy.want(), strategy.address, {"from": test_strategist})
    assert controller.strategies(strategy.want()) == strategy.address

