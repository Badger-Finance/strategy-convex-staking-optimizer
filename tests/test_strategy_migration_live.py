import brownie
import pytest
import json
from brownie import (
    StrategyConvexStakingOptimizer,
    Controller,
    accounts,
    interface,
)
from config.badger_config import badger_config
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

HELPER_STRATS = ["native.cvx","native.cvxCrv"]

NEW_STRATEGIES = {
    "native.renCrv": "0xe66dB6Eb807e6DAE8BD48793E9ad0140a2DEE22A",
    "native.sbtcCrv": "0x2f278515425c8eE754300e158116930B8EcCBBE1",
    "native.tbtcCrv": "0x9e0742EE7BECde52A5494310f09aad639AA4790B",
    "native.hbtcCrv": "0x7354D5119bD42a77E7162c8Afa8A1D18d5Da9cF8",
    "native.pbtcCrv": "0x3f98F3a21B125414e4740316bd6Ef14718764a22",
    "native.obtcCrv": "0x50Dd8A61Bdd11Cf5539DAA83Bc8E0F581eD8110a",
    "native.bbtcCrv": "0xf92660E0fdAfE945aa13616428c9fB4BE19f4d34",
    "native.tricrypto2": "0xf3202Aa2783F3DEE24a35853C6471db065B05D37",
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

    # ==== Parameter comparison ==== #

    # Want matches vault and new Strategy
    assert want == vault.token()
    assert want == newStrategy.want()

    # Check that Slippage tolerance was set on init for new Strategy
    assert newStrategy.crvCvxCrvSlippageToleranceBps() == 500
    assert newStrategy.crvCvxCrvPoolIndex() == 2

    # Check that strategy's constants remain the same
    assert newStrategy.baseRewardsPool() == strategy.baseRewardsPool()
    assert newStrategy.pid() == strategy.pid()
    assert newStrategy.badgerTree() == strategy.badgerTree()
    assert newStrategy.cvxHelperVault() == strategy.cvxHelperVault()
    assert newStrategy.cvxCrvHelperVault() == strategy.cvxCrvHelperVault()
    assert newStrategy.curvePool() == strategy.curvePool()
    assert newStrategy.autoCompoundingBps() == strategy.autoCompoundingBps()
    assert (
        newStrategy.autoCompoundingPerformanceFeeGovernance()
        == strategy.autoCompoundingPerformanceFeeGovernance()
    )
    assert newStrategy.autoCompoundingPerformanceFeeGovernance() == (
        strategy.autoCompoundingPerformanceFeeGovernance()
    )

    # Check that strategy's parameters remain the same
    assert newStrategy.want() == strategy.want()
    assert newStrategy.strategist() == "0x86cbD0ce0c087b482782c181dA8d191De18C8275" # Tech Ops Multisig
    assert newStrategy.keeper() == "0x711A339c002386f9db409cA55b6A35a604aB6cF6" # Keeper ACL
    assert newStrategy.guardian() == "0x6615e67b8B6b6375D38A0A3f937cd8c1a1e96386" # WarRoom ACL

    assert newStrategy.performanceFeeGovernance() == strategy.performanceFeeGovernance()
    assert newStrategy.performanceFeeStrategist() == strategy.performanceFeeStrategist()
    assert newStrategy.withdrawalFee() == strategy.withdrawalFee()
    console.print('\n', f"[green]Fees Match![/green]")
    console.print(f"GovPerformance: {strategy.performanceFeeGovernance()}")
    console.print(f"StrategistPerformance: {strategy.performanceFeeStrategist()}")
    console.print(f"Withdrawal: {strategy.withdrawalFee()}")

    # ==== Pre-Migration checks ==== #

    # Initial balance on New Strategy - In case there's any
    initialStratBalance = newStrategy.balanceOf()
    # Balance of Sett (Balance on Sett, Controller and Strategy) is greater than 0
    initialSettBalance = vault.balance()
    assert initialSettBalance > 0
    # Balance of vault equals to the Sett's balance minus strategy balance
    assert (
        want.balanceOf(vault.address)
        == initialSettBalance - strategy.balanceOf()
    )
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


def migrate_strategy(
    strategy,
    newStrategy,
    controller,
    governance
):
    console.print(f"[blue]Migrating strategy[/blue]")
    # Approve new strategy for want on Controller
    controller.approveStrategy(strategy.want(), newStrategy.address, {"from": governance})
    assert controller.approvedStrategies(strategy.want(), newStrategy.address)

    # Set new strategy for want on Controller
    controller.setStrategy(strategy.want(), newStrategy.address, {"from": governance})
    assert controller.strategies(strategy.want()) == newStrategy.address


