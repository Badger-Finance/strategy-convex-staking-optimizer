import brownie
from brownie import *
from helpers.constants import MaxUint256
from helpers.SnapshotManager import SnapshotManager
from helpers.time import days
from helpers.utils import (
    approx,
)
from config.badger_config import sett_config
import pytest
from conftest import deploy

"""
  TODO: Put your tests here to prove the strat is good!
  See test_harvest_flow, for the basic tests
  See test_strategy_permissions, for tests at the permissions level
"""

@pytest.mark.parametrize(
    "sett_id",
    sett_config.native,
)
def test_are_you_trying(sett_id):
    """
    Verifies that you set up the Strategy properly
    """
    # Setup
    deployed = deploy(sett_config.native[sett_id])

    deployer = deployed.deployer
    sett = deployed.sett
    want = deployed.want
    strategy = deployed.strategy

    startingBalance = want.balanceOf(deployer)

    depositAmount = startingBalance // 2
    assert startingBalance >= depositAmount
    assert startingBalance >= 0
    assert want.balanceOf(sett) == 0

    want.approve(sett, MaxUint256, {"from": deployer})
    sett.deposit(depositAmount, {"from": deployer})

    available = sett.available()
    assert available > 0

    sett.earn({"from": deployer})

    chain.sleep(10000 * 13)  # Mine so we get some interest

    ## TEST 1: Does the want get used in any way?
    assert want.balanceOf(sett) == depositAmount - available

    # Did the strategy do something with the asset?
    assert want.balanceOf(strategy) < available

    ## End Setup

    harvest = strategy.harvest({"from": deployer})

    ## Assert perFee for governance is exactly 20% // Round because huge numbers
    assert approx(
        (
            harvest.events["PerformanceFeeGovernance"][0]["amount"]
            + harvest.events["TreeDistribution"][0]["amount"]
        )
        * (sett_config.native[sett_id].params.performanceFeeGovernance / 10000),
        harvest.events["PerformanceFeeGovernance"][0]["amount"],
        1,
    )

    ## Fail if PerformanceFeeStrategist is fired
    try:
        harvest.events["PerformanceFeeStrategist"]
        assert False
    except:
        assert True

    ## The fee is in bveCVX
    assert harvest.events["PerformanceFeeGovernance"][0]["token"] == strategy.cvxCrvHelperVault()


@pytest.mark.parametrize(
    "sett_id",
    sett_config.native,
)
def test_fee_configs(sett_id):
    """
    Checks the fees are processed properly according to 
    different configurations.
    """
    # Setup
    deployed = deploy(sett_config.native[sett_id])

    deployer = deployed.deployer
    governance = deployed.governance
    sett = deployed.sett
    want = deployed.want
    strategy = deployed.strategy

    startingBalance = want.balanceOf(deployer)

    depositAmount = startingBalance // 2
    assert startingBalance >= depositAmount
    assert startingBalance >= 0
    assert want.balanceOf(sett) == 0

    want.approve(sett, MaxUint256, {"from": deployer})
    sett.deposit(depositAmount, {"from": deployer})

    available = sett.available()
    assert available > 0

    sett.earn({"from": deployer})

    chain.sleep(10000 * 13)  # Mine so we get some interest

    ## End Setup

    chain.snapshot()

    # TEST 1: Configures Gov Fee/Strategist Fee: 20%/0%
    strategy.setPerformanceFeeGovernance(2000, {"from": governance})
    strategy.setPerformanceFeeStrategist(0, {"from": governance})

    harvest = strategy.harvest({"from": deployer})

    ## Fees are being processed
    assert harvest.events["PerformanceFeeGovernance"][0]["amount"] > 0
    assert harvest.events["PerformanceFeeGovernance"][1]["amount"] > 0

    ## Fail if PerformanceFeeStrategist is fired
    try:
        harvest.events["PerformanceFeeStrategist"]
        assert False
    except:
        assert True

    ## The fees are in CRV and CVX
    assert harvest.events["PerformanceFeeGovernance"][0]["token"] == strategy.cvxCrvHelperVault()
    assert harvest.events["PerformanceFeeGovernance"][1]["token"] == strategy.bveCVX()


    chain.revert()

    # TEST 2: Configures Gov Fee/Strategist Fee: 10%/10%
    strategy.setPerformanceFeeGovernance(1000, {"from": governance})
    strategy.setPerformanceFeeStrategist(1000, {"from": governance})

    harvest = strategy.harvest({"from": deployer})

    ## Fees are being processed
    assert harvest.events["PerformanceFeeGovernance"][0]["amount"] > 0
    assert harvest.events["PerformanceFeeGovernance"][1]["amount"] > 0
    assert harvest.events["PerformanceFeeStrategist"][0]["amount"] > 0
    assert harvest.events["PerformanceFeeStrategist"][1]["amount"] > 0

    # Both fees are equal
    assert (
        harvest.events["PerformanceFeeGovernance"][0]["amount"]
    ) == (
        harvest.events["PerformanceFeeStrategist"][0]["amount"]
    )
    assert (
        harvest.events["PerformanceFeeGovernance"][1]["amount"]
    ) == (
        harvest.events["PerformanceFeeStrategist"][1]["amount"]
    )

    ## The fees are in CRV and CVX
    assert harvest.events["PerformanceFeeGovernance"][0]["token"] == strategy.cvxCrvHelperVault()
    assert harvest.events["PerformanceFeeGovernance"][1]["token"] == strategy.bveCVX()
    assert harvest.events["PerformanceFeeStrategist"][0]["token"] == strategy.cvxCrvHelperVault()
    assert harvest.events["PerformanceFeeStrategist"][1]["token"] == strategy.bveCVX()


    chain.revert()

    # TEST 3: Configures Gov Fee/Strategist Fee: 0%/20%
    strategy.setPerformanceFeeGovernance(0, {"from": governance})
    strategy.setPerformanceFeeStrategist(2000, {"from": governance})

    harvest = strategy.harvest({"from": deployer})

    ## Fees are being processed
    assert harvest.events["PerformanceFeeStrategist"][0]["amount"] > 0
    assert harvest.events["PerformanceFeeStrategist"][1]["amount"] > 0

    ## Fail if PerformanceFeeGovernance is fired
    try:
        harvest.events["PerformanceFeeGovernance"]
        assert False
    except:
        assert True

    ## The fees are in CRV and CVX
    assert harvest.events["PerformanceFeeStrategist"][0]["token"] == strategy.cvxCrvHelperVault()
    assert harvest.events["PerformanceFeeStrategist"][1]["token"] == strategy.bveCVX()
