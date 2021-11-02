from brownie import (
    accounts,
    interface,
    Controller,
    SettV4,
    StrategyConvexStakingOptimizer,
)
from config import (
    BADGER_DEV_MULTISIG,
    CURVE_POOL_CONFIG,
    PID,
    WANT,
    FEES,
    WANT_CONFIG,
)
from dotmap import DotMap
import pytest


@pytest.fixture(autouse=True)
def isolation(fn_isolation):
    pass


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
    controller.initialize(BADGER_DEV_MULTISIG, strategist, keeper, BADGER_DEV_MULTISIG)

    sett = SettV4.deploy({"from": deployer})
    sett.initialize(
        WANT,
        controller,
        BADGER_DEV_MULTISIG,
        keeper,
        guardian,
        False,
        "prefix",
        "PREFIX",
    )

    sett.unpause({"from": governance})
    controller.setVault(WANT, sett)

    ## Start up Strategy
    strategy = StrategyConvexStakingOptimizer.deploy({"from": deployer})
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
    )

    ## Grant contract access from strategy to Helper Vaults
    cvxHelperVault = SettV4.at(strategy.cvxHelperVault())
    cvxCrvHelperVault = SettV4.at(strategy.cvxCrvHelperVault())

    cvxHelperGov = accounts.at(cvxHelperVault.governance(), force=True)
    cvxCrvHelperGov = accounts.at(cvxCrvHelperVault.governance(), force=True)

    cvxHelperVault.approveContractAccess(strategy.address, {"from": cvxHelperGov})
    cvxCrvHelperVault.approveContractAccess(strategy.address, {"from": cvxCrvHelperGov})

    ## Set up tokens
    want = interface.IERC20(WANT)

    ## Wire up Controller to Strart
    ## In testing will pass, but on live it will fail
    controller.approveStrategy(WANT, strategy, {"from": governance})
    controller.setStrategy(WANT, strategy, {"from": deployer})

    # Transfer test assets to deployer
    whale = accounts.at(
        "0x647481c033A4A2E816175cE115a0804adf793891", force=True
    )  # RenCRV whale
    want.transfer(
        deployer.address, want.balanceOf(whale.address), {"from": whale}
    )  # Transfer 80% of whale's want balance

    assert want.balanceOf(deployer.address) > 0

    return DotMap(
        deployer=deployer,
        controller=controller,
        vault=sett,
        sett=sett,
        strategy=strategy,
        want=want,
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
