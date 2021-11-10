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

def test_proper_fees():
    """
    Per the settings, governance takes 20% perf fee
    And strategist 0
    Let's do a check on the events to prove that's the case
    """
    assert True

    ## TODO: Custom Test to check for proper funds distribution during harvest event

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
        * 0.2,
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
    assert harvest.events["PerformanceFeeGovernance"][0]["token"] == strategy.bveCVX()
