## Ideally, they have one file with the settings for the strat and deployment
## This file would allow them to configure so they can test, deploy and interact with the strategy

BADGER_DEV_MULTISIG = "0xb65cef03b9b89f99517643226d76e286ee999e77"

# Using RenCRV parameters for testing
WANT = "0xF3A43307DcAFa93275993862Aae628fCB50dC768"  ## cvxFVX/FXS crv
BADGER_TREE = "0x660802Fc641b154aBA66a62137e71f331B6d787A"  ## badgerTree
CVXHELPER = "0x53c8e199eb2cb7c01543c137078a038937a68e40"  ## cvxHelperVault
CVXCRVHELPER = "0x2B5455aac8d64C14786c3a29858E43b5945819C0"  ## cvxCrvHelperVault

# Want config array
WANT_CONFIG = [WANT, BADGER_TREE, CVXHELPER, CVXCRVHELPER]

# cvxFXS/FXS
PID = 72

## Fees in Basis Points
DEFAULT_GOV_PERFORMANCE_FEE = 2000
DEFAULT_PERFORMANCE_FEE = 0
DEFAULT_WITHDRAWAL_FEE = 1

CURVE_POOL_CONFIG = [
    "0xF3A43307DcAFa93275993862Aae628fCB50dC768",  # Swap Contract
    1,  # WBTC position
    2,  # Num of Elements
]

FEES = [DEFAULT_GOV_PERFORMANCE_FEE, DEFAULT_PERFORMANCE_FEE, DEFAULT_WITHDRAWAL_FEE]

REGISTRY = "0xFda7eB6f8b7a9e9fCFd348042ae675d1d652454f"  # Multichain BadgerRegistry
