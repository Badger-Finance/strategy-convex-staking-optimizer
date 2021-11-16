import brownie
import pytest
import json
from brownie import (
    StrategyConvexStakingOptimizer,
    SettV4,
    Controller,
    accounts,
    interface,
    chain
)
from config.badger_config import badger_config
from rich.console import Console
from helpers.SnapshotManager import SnapshotManager
from helpers.utils import get_config
from helpers.constants import MaxUint256
from helpers.time import days
import time


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

NEW_STRATEGIES = {
    "native.renCrv": "0x61e16b46F74aEd8f9c2Ec6CB2dCb2258Bdfc7071",
    "native.sbtcCrv": "0xCce0D2d1Eb2310F7e67e128bcFE3CE870A3D3a3d",
    "native.tbtcCrv": "0xAB73Ec65a1Ef5a2e5b56D5d6F36Bee4B2A1D3FFb",
    "native.hbtcCrv": "0x8c26D9B6B80684CC642ED9eb1Ac1729Af3E819eE",
    "native.pbtcCrv": "0xA9A646668Df5Cec5344941646F5c6b269551e53D",
    "native.obtcCrv": "0x5dd69c6D81f0a403c03b99C5a44Ef2D49b66d388",
    "native.bbtcCrv": "0xF2F3AB09E2D8986fBECbBa59aE838a5418a6680c",
    "native.tricrypto2": "0x647eeb5C5ED5A71621183f09F6CE8fa66b96827d",
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
def keeper(badger_deploy):
    return accounts.at(badger_deploy["keeper"], force=True)


@pytest.fixture()
def governance_multi(badger_deploy):
    return accounts.at(badger_deploy["devMultisig"], force=True)


@pytest.fixture()
def timelock(badger_deploy):
    return accounts.at(badger_deploy["timelock"], force=True)


@pytest.fixture()
def exp_controller(badger_deploy):
    return Controller.at(badger_deploy["sett_system"]["controllers"]["experimental"])


@pytest.fixture()
def native_controller(badger_deploy):
    return Controller.at(badger_deploy["sett_system"]["controllers"]["native"])


@pytest.fixture()
def strategies(badger_deploy):
    return badger_deploy["sett_system"]["strategies"]


@pytest.fixture()
def vaults(badger_deploy):
    return badger_deploy["sett_system"]["vaults"]


@pytest.mark.parametrize(
    "strategy_key",
    STRAT_KEYS,
)
def test_migrate_staking_optimizer(
    strategy_key,
    timelock,
    exp_controller,
    native_controller,
    strategies,
    vaults,
):

    # Different Setts use different controllers:
    if strategy_key in ["native.renCrv", "native.sbtcCrv", "native.tbtcCrv"]:
        governance = timelock
        controller = native_controller
    else:
        governance = timelock
        controller = exp_controller

    console.print(f"[yellow]Processing {strategy_key}...[/yellow]")

    # Get current strategy
    strategy = interface.IStrategyConvexStakingOptimizer(strategies[strategy_key])
    # Get vault
    vault = interface.ISettV4(vaults[strategy_key])
    # Get new strategy
    newStrategy = StrategyConvexStakingOptimizer.at(NEW_STRATEGIES[strategy_key])
    # Get want
    want = interface.IERC20(strategy.want())

    console.print(f"[blue]Current Strategy: [/blue]{strategy.address}")
    console.print(f"[blue]New Strategy: [/blue]{newStrategy.address}")
    console.print(f"[blue]Vault: [/blue]{vault.address}")
    console.print(f"[blue]Want: [/blue]{want.address}")

    # Run pre-migration setup actions (to be executed IRL)
    setup_actions(controller, newStrategy)

    # ==== Parameter comparison ==== #

    # Want matches vault and new Strategy
    assert want == vault.token()
    assert want == newStrategy.want()

    # Check that Slippage tolerance was set on init for new Strategy
    assert newStrategy.stableSwapSlippageTolerance() == 500
    assert newStrategy.crvCvxCrvPoolIndex() == 2

    # Check that strategy's constants remain the same
    assert newStrategy.baseRewardsPool() == strategy.baseRewardsPool()
    assert newStrategy.pid() == strategy.pid()
    assert newStrategy.badgerTree() == strategy.badgerTree()
    assert newStrategy.cvxCrvHelperVault() == strategy.cvxCrvHelperVault()
    assert newStrategy.curvePool() == strategy.curvePool()
    assert newStrategy.autoCompoundingBps() == strategy.autoCompoundingBps()
    assert (
        newStrategy.autoCompoundingPerformanceFeeGovernance()
        == 0
    )

    # Check that strategy's parameters remain the same
    assert newStrategy.want() == strategy.want()
    assert (
        newStrategy.strategist() == "0x86cbD0ce0c087b482782c181dA8d191De18C8275"
    )  # Tech Ops Multisig
    assert (
        newStrategy.keeper() == "0x711A339c002386f9db409cA55b6A35a604aB6cF6"
    )  # Keeper ACL
    assert (
        newStrategy.guardian() == "0x6615e67b8B6b6375D38A0A3f937cd8c1a1e96386"
    )  # WarRoom ACL

    assert newStrategy.performanceFeeGovernance() == 2000
    assert newStrategy.performanceFeeStrategist() == strategy.performanceFeeStrategist()
    assert newStrategy.withdrawalFee() == strategy.withdrawalFee()
    console.print(f"\n[green]Fees Match![/green]")
    console.print(f"GovPerformance: {strategy.performanceFeeGovernance()}")
    console.print(f"StrategistPerformance: {strategy.performanceFeeStrategist()}")
    console.print(f"Withdrawal: {strategy.withdrawalFee()}")

    ## Change governance fees to native (Council vote):
    stratGov = accounts.at(newStrategy.governance(), force=True)
    newStrategy.setAutoCompoundingPerformanceFeeGovernance(0, {"from": stratGov})
    assert newStrategy.autoCompoundingPerformanceFeeGovernance() == 0
    newStrategy.setPerformanceFeeGovernance(2000, {"from": stratGov})
    assert newStrategy.performanceFeeGovernance() == 2000
    console.print("[green]Autocompunding and governance fees were changed![/green]")

    # ==== Pre-Migration checks ==== #

    # Initial balance on New Strategy - In case there's any
    initialStratBalance = newStrategy.balanceOf()
    # Balance of Sett (Balance on Sett, Controller and Strategy) is greater than 0
    initialSettBalance = vault.balance()
    assert initialSettBalance > 0
    # Balance of vault equals to the Sett's balance minus strategy balance
    assert want.balanceOf(vault.address) == initialSettBalance - strategy.balanceOf()
    # PPFS before migration
    ppfs = vault.getPricePerFullShare()

    # ==== Migration ==== #
    migrate_strategy(
        strategy,
        newStrategy,
        controller,
        governance,
    )

    # ==== Post-Migration checks ==== #

    # Total sett balance is intial balance on sett plus initial balance on new Strat
    assert initialSettBalance + initialStratBalance == vault.balance()
    # Balance of vault equals to the whole Sett balance since controller withdraws all of want
    # and this is transfered to the vault.
    assert want.balanceOf(vault.address) == initialSettBalance
    # Balance of old Strategy goes down to 0
    assert strategy.balanceOf() == 0
    # Balance of new Strategy starts off at 0
    assert newStrategy.balanceOf() == initialStratBalance
    # PPS are equal or higher post migration (in case there was want on newStrat)
    assert vault.getPricePerFullShare() >= ppfs

    console.print(f"[green]Strategy migrated successfully![/green]")
    
    chain.sleep(1000)
    chain.mine()

    user_deposit_withdraw_harvest_flow(
        strategy_key,
        vault,
        newStrategy,
        controller,
    )

def migrate_strategy(strategy, newStrategy, controller, governance):
    console.print(f"[blue]Migrating strategy[/blue]")
    # Approve new strategy for want on Controller
    controller.approveStrategy(
        strategy.want(), newStrategy.address, {"from": governance}
    )
    assert controller.approvedStrategies(strategy.want(), newStrategy.address)

    # Set new strategy for want on Controller
    controller.setStrategy(strategy.want(), newStrategy.address, {"from": governance})
    assert controller.strategies(strategy.want()) == newStrategy.address

# Execute migration setup txs while they get executed IRL
def setup_actions(controller, newStrategy):

    # Set production controller on strat
    if newStrategy.controller() != controller.address:
        stratGov = accounts.at(newStrategy.governance(), force=True)
        newStrategy.setController(controller.address, {"from": stratGov})

    # Change strategist to Tech Ops
    if newStrategy.strategist() != "0x86cbD0ce0c087b482782c181dA8d191De18C8275":
        newStrategy.setStrategist("0x86cbD0ce0c087b482782c181dA8d191De18C8275", {"from": stratGov})

    # Grant contract access from strategy to cvxCRV Helper Vault
    cvxCrvHelperVault = SettV4.at(newStrategy.cvxCrvHelperVault())
    cvxCrvHelperGov = accounts.at(cvxCrvHelperVault.governance(), force=True)
    cvxCrvHelperVault.approveContractAccess(newStrategy.address, {"from": cvxCrvHelperGov})

# User flow deposits, withdraws, earns, tends and harvests to ensure that strategy still works
def user_deposit_withdraw_harvest_flow(
    strategy_key,
    vault,
    strategy,
    controller,
):
    snap = SnapshotManager(vault, strategy, controller, "StrategySnapshot")
    keeper = accounts.at(strategy.keeper(), force=True) # Should be the same on the vault
    randomUser = accounts[0]

    want = interface.IERC20(strategy.want())

    config = get_config(strategy_key)
    # Transfer test assets to user
    whale = accounts.at(
        config.whale, force=True
    )
    want.transfer(
        randomUser.address, want.balanceOf(whale.address), {"from": whale}
    )  # Transfer 80% of whale's want balance

    startingBalance = want.balanceOf(randomUser)
    depositAmount = startingBalance // 2
    assert startingBalance >= depositAmount
    assert startingBalance >= 0
    # End Setup

    ## Reset rewards if they are set to expire within the next 4 days or are expired already
    rewardsPool = interface.IBaseRewardsPool(strategy.baseRewardsPool())
    if rewardsPool.periodFinish() - int(time.time()) < days(4):
        booster = interface.IBooster(strategy.booster())
        booster.earmarkRewards(config.params.pid, {"from": randomUser})
        console.print("[green]BaseRewardsPool expired or expiring soon - it was reset![/green]")

    # Run post migration flow
    snap.settEarn({"from": keeper})

    # User has no balance on Sett and shouldn't be able to withdraw
    with brownie.reverts():
        strategy.withdrawAll({"from": randomUser})

    chain.sleep(3600)
    chain.mine()

    snap.settTend({"from": keeper})

    chain.sleep(3600)
    chain.mine()

    snap.settHarvest({"from": keeper})

    chain.sleep(days(3))
    chain.mine()

    ## Reset rewards if they are set to expire within the next 4 days or are expired already
    rewardsPool = interface.IBaseRewardsPool(strategy.baseRewardsPool())
    if rewardsPool.periodFinish() - int(time.time()) < days(4):
        booster = interface.IBooster(strategy.booster())
        booster.earmarkRewards(config.params.pid, {"from": randomUser})
        console.print("[green]BaseRewardsPool expired or expiring soon - it was reset![/green]")

    want.approve(vault, MaxUint256, {"from": randomUser})
    snap.settDeposit(depositAmount, {"from": randomUser})
    shares = vault.balanceOf(randomUser)

    chain.sleep(3600)
    chain.mine()

    snap.settEarn({"from": keeper})

    chain.sleep(3600)
    chain.mine()

    snap.settTend({"from": keeper})

    chain.sleep(3600)
    chain.mine()

    snap.settWithdraw(shares // 2, {"from": randomUser})

    chain.sleep(days(3))
    chain.mine()

    snap.settHarvest({"from": keeper})

    chain.sleep(3600)
    chain.mine()

    snap.settWithdraw(shares // 2 - 1, {"from": randomUser})





