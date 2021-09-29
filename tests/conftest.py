from brownie import (
    accounts,
    interface,
    Controller,
    SettV3,
    MyStrategy,
)
from config import (
    BADGER_DEV_MULTISIG,
    CURVE_POOL_CONFIG,
    PID,
    WANT,
    FEES,
    WANT_CONFIG,
    CVXHELPER,
    CVXCRVHELPER
)
from dotmap import DotMap
import pytest
from helpers.constants import MaxUint256

@pytest.fixture
def deployed():
    """
    Deploys, vault, controller and strats and wires them up for you to test
    """
    deployer = accounts[0]

    strategist = deployer
    keeper = deployer
    guardian = deployer

    governance = accounts.at(BADGER_DEV_MULTISIG, force=True)

    controller = Controller.deploy({"from": deployer})
    controller.initialize(BADGER_DEV_MULTISIG, strategist, keeper, BADGER_DEV_MULTISIG, {'from': governance })

    sett = SettV3.deploy({"from": deployer})
    sett.initialize(
        WANT,
        controller,
        BADGER_DEV_MULTISIG,
        keeper,
        guardian,
        False,
        "prefix",
        "PREFIX",
        {'from': governance }
    )

    sett.unpause({"from": governance})
    controller.setVault(WANT, sett)

    ## TODO: Add guest list once we find compatible, tested, contract
    # guestList = VipCappedGuestListWrapperUpgradeable.deploy({"from": deployer})
    # guestList.initialize(sett, {"from": deployer})
    # guestList.setGuests([deployer], [True])
    # guestList.setUserDepositCap(100000000)
    # sett.setGuestList(guestList, {"from": governance})

    ## Start up Strategy
    strategy = MyStrategy.deploy({"from": deployer})
    strategy.initialize(
        governance,
        strategist,
        controller,
        keeper,
        guardian,
        WANT_CONFIG,
        PID,
        FEES,
        CURVE_POOL_CONFIG,
        {'from': governance }
    )

    strategy.setMinPoolHarvest(0, 0, 0, 0, {"from": governance})

    ## Tool that verifies bytecode (run independently) <- Webapp for anyone to verify

    ## Set up tokens
    want = interface.IERC20(WANT)

    ## Wire up Controller to Strart
    ## In testing will pass, but on live it will fail
    controller.approveStrategy(WANT, strategy, {"from": governance})
    controller.setStrategy(WANT, strategy, {"from": deployer})

    # Transfer test assets to deployer
    whale = accounts.at("0x647481c033A4A2E816175cE115a0804adf793891", force=True) # RenCRV whale
    want.transfer(deployer.address, want.balanceOf(whale.address), {"from": whale}) # Transfer 80% of whale's want balance

    # CurveSwapper to generate fees
    swapper = interface.ICurveExchange("0x73FC48a7144db8Ee6576D99676b63Db458527717")

    assert want.balanceOf(deployer.address) > 0

    # Turn on permissions for deployer
    cvxhelper = interface.IERC20(CVXHELPER)
    cvxhelper.approve(deployer.address, MaxUint256, {'from': deployer})
    cvxhelper.approve(controller.rewards(), MaxUint256, {'from': controller.rewards()})
    cvxcrvhelper = interface.IERC20(CVXCRVHELPER)
    cvxcrvhelper.approve(deployer.address, MaxUint256, {'from': deployer})
    cvxcrvhelper.approve(controller.rewards(), MaxUint256, {'from': controller.rewards()})

    sett.approveContractAccess( controller, { 'from': governance } )
    sett.approveContractAccess( controller.rewards(), { 'from': governance } )
    sett.approveContractAccess( deployer , { 'from': governance } )

    cvxhelper = interface.ISettAccessControlDefended(CVXHELPER)
    cvxcrvhelper = interface.ISettAccessControlDefended(CVXCRVHELPER)
    cvxhelper.approveContractAccess( strategy , { 'from': governance } )
    cvxcrvhelper.approveContractAccess( strategy , { 'from': governance } )

    return DotMap(
        deployer=deployer,
        controller=controller,
        vault=sett,
        sett=sett,
        strategy=strategy,
        # guestList=guestList,
        want=want,
        swapper=swapper,
    )


## Contracts ##


@pytest.fixture
def vault(deployed):
    return deployed.vault


@pytest.fixture
def sett(deployed):
    return deployed.sett


@pytest.fixture
def controller(deployed):
    return deployed.controller


@pytest.fixture
def strategy(deployed):
    return deployed.strategy

@pytest.fixture
def swapper(deployed):
    return deployed.swapper

## Tokens ##


@pytest.fixture
def want(deployed):
    return deployed.want


@pytest.fixture
def tokens():
    return [WANT]

## Accounts ##


@pytest.fixture
def deployer(deployed):
    return deployed.deployer


@pytest.fixture
def strategist(strategy):
    return accounts.at(strategy.strategist(), force=True)


@pytest.fixture
def settKeeper(vault):
    return accounts.at(vault.keeper(), force=True)


@pytest.fixture
def strategyKeeper(strategy):
    return accounts.at(strategy.keeper(), force=True)