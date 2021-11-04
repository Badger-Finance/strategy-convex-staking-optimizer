// SPDX-License-Identifier: MIT

pragma solidity ^0.6.0;
pragma experimental ABIEncoderV2;

interface IStrategyConvexStakingOptimizer {
    event ExtraRewardsTokenSet(
        address indexed token,
        uint256 autoCompoundingBps,
        uint256 autoCompoundingPerfFee,
        uint256 treeDistributionPerfFee,
        address tendConvertTo,
        uint256 tendConvertBps
    );
    event Harvest(uint256 harvested, uint256 indexed blockNumber);
    event Paused(address account);
    event PerformanceFeeGovernance(
        address indexed destination,
        address indexed token,
        uint256 amount,
        uint256 indexed blockNumber,
        uint256 timestamp
    );
    event PerformanceFeeStrategist(
        address indexed destination,
        address indexed token,
        uint256 amount,
        uint256 indexed blockNumber,
        uint256 timestamp
    );
    event SetController(address controller);
    event SetGovernance(address governance);
    event SetPerformanceFeeGovernance(uint256 performanceFeeGovernance);
    event SetPerformanceFeeStrategist(uint256 performanceFeeStrategist);
    event SetStrategist(address strategist);
    event SetWithdrawalFee(uint256 withdrawalFee);
    event Tend(uint256 tended);
    event TendState(uint256 crvTended, uint256 cvxTended, uint256 cvxCrvTended);
    event TokenSwapPathSet(address tokenIn, address tokenOut, address[] path);
    event TreeDistribution(
        address indexed token,
        uint256 amount,
        uint256 indexed blockNumber,
        uint256 timestamp
    );
    event Unpaused(address account);
    event Withdraw(uint256 amount);
    event WithdrawAll(uint256 balance);
    event WithdrawOther(address token, uint256 amount);
    event WithdrawState(
        uint256 toWithdraw,
        uint256 preWant,
        uint256 postWant,
        uint256 withdrawn
    );

    function AUTO_COMPOUNDING_BPS() external view returns (uint256);

    function AUTO_COMPOUNDING_PERFORMANCE_FEE() external view returns (uint256);

    function CVX_ETH_SLP() external view returns (address);

    function CVX_ETH_SLP_Pid() external view returns (uint256);

    function MAX_FEE() external view returns (uint256);

    function MAX_UINT_256() external view returns (uint256);

    function __BaseStrategy_init(
        address _governance,
        address _strategist,
        address _controller,
        address _keeper,
        address _guardian
    ) external;

    function addExtraRewardsToken(
        address _extraToken,
        StrategyConvexStakingOptimizer.RewardTokenConfig
            calldata _rewardsConfig,
        address[] calldata _swapPathToWant
    ) external;

    function autoCompoundingBps() external view returns (uint256);

    function autoCompoundingPerformanceFeeGovernance()
        external
        view
        returns (uint256);

    function badgerTree() external view returns (address);

    function balanceOf() external view returns (uint256);

    function balanceOfPool() external view returns (uint256);

    function balanceOfWant() external view returns (uint256);

    function baseRewardsPool() external view returns (address);

    function baseStrategyVersion() external view returns (string memory);

    function booster() external view returns (address);

    function bveCVX() external view returns (address);

    function controller() external view returns (address);

    function convexMasterChef() external view returns (address);

    function crv() external view returns (address);

    function crvDepositor() external view returns (address);

    function crvToken() external view returns (address);

    function curvePool()
        external
        view
        returns (
            address swap,
            uint256 wbtcPosition,
            uint256 numElements
        );

    function cvx() external view returns (address);

    function cvxCRV_CRV_SLP() external view returns (address);

    function cvxCRV_CRV_SLP_Pid() external view returns (uint256);

    function cvxCrv() external view returns (address);

    function cvxCrvHelperVault() external view returns (address);

    function cvxCrvRewardsPool() external view returns (address);

    function cvxCrvToken() external view returns (address);

    function cvxHelperVault() external view returns (address);

    function cvxRewardsPool() external view returns (address);

    function cvxToken() external view returns (address);

    function deposit() external;

    function getName() external pure returns (string memory);

    function getProtectedTokens() external view returns (address[] memory);

    function getTokenSwapPath(address tokenIn, address tokenOut)
        external
        view
        returns (address[] memory);

    function governance() external view returns (address);

    function guardian() external view returns (address);

    function harvest()
        external
        returns (StrategyConvexStakingOptimizer.HarvestData memory);

    function initialize(
        address _governance,
        address _strategist,
        address _controller,
        address _keeper,
        address _guardian,
        address[4] calldata _wantConfig,
        uint256 _pid,
        uint256[3] calldata _feeConfig,
        StrategyConvexStakingOptimizer.CurvePoolConfig calldata _curvePool
    ) external;

    function initializeApprovals() external;

    function isProtectedToken(address token) external view returns (bool);

    function isTendable() external view returns (bool);

    function keeper() external view returns (address);

    function pause() external;

    function paused() external view returns (bool);

    function performanceFeeGovernance() external view returns (uint256);

    function performanceFeeStrategist() external view returns (uint256);

    function pid() external view returns (uint256);

    function removeExtraRewardsToken(address _extraToken) external;

    function rewardsTokenConfig(address)
        external
        view
        returns (
            uint256 autoCompoundingBps,
            uint256 autoCompoundingPerfFee,
            uint256 treeDistributionPerfFee,
            address tendConvertTo,
            uint256 tendConvertBps
        );

    function setAutoCompoundingBps(uint256 _bps) external;

    function setAutoCompoundingPerformanceFeeGovernance(uint256 _bps) external;

    function setController(address _controller) external;

    function setCurvePoolSwap(address _swap) external;

    function setGovernance(address _governance) external;

    function setGuardian(address _guardian) external;

    function setKeeper(address _keeper) external;

    function setPerformanceFeeGovernance(uint256 _performanceFeeGovernance)
        external;

    function setPerformanceFeeStrategist(uint256 _performanceFeeStrategist)
        external;

    function setPid(uint256 _pid) external;

    function setStrategist(address _strategist) external;

    function setWithdrawalFee(uint256 _withdrawalFee) external;

    function setWithdrawalMaxDeviationThreshold(uint256 _threshold) external;

    function strategist() external view returns (address);

    function tend()
        external
        returns (StrategyConvexStakingOptimizer.TendData memory);

    function threeCrv() external view returns (address);

    function threeCrvSwap() external view returns (address);

    function threeCrvToken() external view returns (address);

    function tokenSwapPaths(
        address,
        address,
        uint256
    ) external view returns (address);

    function unpause() external;

    function usdc() external view returns (address);

    function usdcToken() external view returns (address);

    function version() external pure returns (string memory);

    function want() external view returns (address);

    function wbtc() external view returns (address);

    function wbtcToken() external view returns (address);

    function weth() external view returns (address);

    function withdraw(uint256 _amount) external;

    function withdrawAll() external returns (uint256 balance);

    function withdrawOther(address _asset) external returns (uint256 balance);

    function withdrawalFee() external view returns (uint256);

    function withdrawalMaxDeviationThreshold() external view returns (uint256);
}

interface StrategyConvexStakingOptimizer {
    struct RewardTokenConfig {
        uint256 autoCompoundingBps;
        uint256 autoCompoundingPerfFee;
        uint256 treeDistributionPerfFee;
        address tendConvertTo;
        uint256 tendConvertBps;
    }

    struct HarvestData {
        uint256 cvxCrvHarvested;
        uint256 cvxHarvsted;
    }

    struct CurvePoolConfig {
        address swap;
        uint256 wbtcPosition;
        uint256 numElements;
    }

    struct TendData {
        uint256 crvTended;
        uint256 cvxTended;
        uint256 cvxCrvTended;
    }
}
