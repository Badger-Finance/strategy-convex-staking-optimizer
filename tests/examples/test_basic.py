from config import (
    BADGER_DEV_MULTISIG,
)
from config.badger_config import sett_config
import pytest
from conftest import deploy

@pytest.mark.parametrize(
    "sett_id",
    sett_config.native,
)
def test_deploy_settings(sett_id):
    """
    Verifies that you set up the Strategy properly
    """
    config = sett_config.native[sett_id]
    deployed = deploy(config)
    
    strategy = deployed.strategy

    protected_tokens = strategy.getProtectedTokens()

    ## NOTE: Change based on how you set your contract
    assert protected_tokens[0] == config.params.want

    assert strategy.governance() == BADGER_DEV_MULTISIG

    assert strategy.performanceFeeGovernance() == 2000
    assert strategy.performanceFeeStrategist() == config.params.performanceFeeStrategist
    assert strategy.withdrawalFee() == config.params.withdrawalFee