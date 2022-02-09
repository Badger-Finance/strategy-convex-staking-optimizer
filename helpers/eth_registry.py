from brownie.network import web3
from dotmap import DotMap
import json


multicall = "0xeefba1e63905ef1d7acba5a8513c70307c1ce441"
multisend = "0x8D29bE29923b68abfDD21e541b9374737B49cdAD"

multichain_registry = DotMap(eth_address="0xC564EE9f21Ed8A2d8E7e76c085740d5e4c5FaFbE")

convex_registry = DotMap(
    cvxHelperVault="0x53c8e199eb2cb7c01543c137078a038937a68e40",
    cvxCrvHelperVault="0x2B5455aac8d64C14786c3a29858E43b5945819C0",
)

curve_registry = DotMap(
    minter="0xd061D61a4d941c39E5453435B6345Dc261C2fcE0",
    crvToken="0xD533a949740bb3306d119CC777fa900bA034cd52",
    symbol="CRV",
    pools=DotMap(
        renCrv=DotMap(
            swap="0x93054188d876f558f4a66B2EF1d97d16eDf0895B",
            token="0x49849C98ae39Fff122806C06791Fa73784FB3675",
            gauge="0xB1F2cdeC61db658F091671F5f199635aEF202CAC",
        ),
        sbtcCrv=DotMap(
            swap="0x7fC77b5c7614E1533320Ea6DDc2Eb61fa00A9714",
            token="0x075b1bb99792c9E1041bA13afEf80C91a1e70fB3",
            gauge="0x705350c4BcD35c9441419DdD5d2f097d7a55410F",
        ),
        tbtcCrv=DotMap(
            swap="0xaa82ca713d94bba7a89ceab55314f9effeddc78c",
            # swap="0xC25099792E9349C7DD09759744ea681C7de2cb66",
            token="0x64eda51d3Ad40D56b9dFc5554E06F94e1Dd786Fd",
            gauge="0x6828bcF74279eE32f2723eC536c22c51Eed383C6",
        ),
        hbtcCrv=DotMap(
            token="0xb19059ebb43466C323583928285a49f558E572Fd",
            gauge="0x4c18E409Dc8619bFb6a1cB56D114C3f592E0aE79",
            swap="0x4CA9b3063Ec5866A4B82E437059D2C43d1be596F",
        ),
        pbtcCrv=DotMap(
            token="0xDE5331AC4B3630f94853Ff322B66407e0D6331E8",
            gauge="0xd7d147c6Bb90A718c3De8C0568F9B560C79fa416",
            swap="0x11F419AdAbbFF8d595E7d5b223eee3863Bb3902C",
        ),
        obtcCrv=DotMap(
            token="0x2fE94ea3d5d4a175184081439753DE15AeF9d614",
            gauge="0x11137B10C210b579405c21A07489e28F3c040AB1",
            swap="0xd5BCf53e2C81e1991570f33Fa881c49EEa570C8D",
        ),
        bbtcCrv=DotMap(
            token="0x410e3E86ef427e30B9235497143881f717d93c2A",
            gauge="0xdFc7AdFa664b08767b735dE28f9E84cd30492aeE",
            swap="0xC45b2EEe6e09cA176Ca3bB5f7eEe7C47bF93c756",
        ),
        triCrypto=DotMap(
            token="0xca3d75ac011bf5ad07a98d02f18225f9bd9a6bdf",
            swap="0x80466c64868E1ab14a1Ddf27A676C3fcBE638Fe5",
            gauge="0x331aF2E331bd619DefAa5DAc6c038f53FCF9F785",
        ),
        triCryptoDos=DotMap(
            token="0xc4AD29ba4B3c580e6D59105FFf484999997675Ff",
            swap="0xD51a44d3FaE010294C616388b506AcdA1bfAAE46",
            gauge="0x3993d34e7e99Abf6B6f367309975d1360222D446",
        ),
        ibbtcCrv=DotMap(
            token="0xFbdCA68601f835b27790D98bbb8eC7f05FDEaA9B",
            swap="0xbba4b444FD10302251d9F5797E763b0d912286A1", # ibBTC
            gauge="0x346C7BB1A7a6A30c8e81c14e90FC2f0FBddc54d8",
        ),
        ustWhCrv=DotMap(
            token="0xCEAF7747579696A2F0bb206a14210e3c9e6fB269",
            swap="0xA79828DF1850E8a3A3064576f380D90aECDD3359", # zap_3pool
            gauge="0xb0f5d00e5916c8b8981e99191A1458704B587b2b",
        ),
    ),
    pids=DotMap(
        renCrv=6,
        sbtcCrv=7,
        tbtcCrv=16,
        hbtcCrv=8,
        pbtcCrv=18,
        obtcCrv=20,
        bbtcCrv=19,
        triCrypto=37,
        triCryptoDos=38,
        ibbtcCrv=53,
        ustWhCrv=59,
    ),
)

tokens = DotMap(
    weth="0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
    wbtc="0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599",
    crv="0xD533a949740bb3306d119CC777fa900bA034cd52",
    tbtc=web3.toChecksumAddress("0x8daebade922df735c38c80c7ebd708af50815faa"),
    usdt=web3.toChecksumAddress("0xdac17f958d2ee523a2206206994597c13d831ec7"),
    dai=web3.toChecksumAddress("0x6b175474e89094c44da98b954eedeac495271d0f"),
    digg="0x798D1bE841a82a273720CE31c822C61a67a601C3",
    usdc=web3.toChecksumAddress("0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48"),
    renbtc=web3.toChecksumAddress("0xeb4c2781e4eba804ce9a9803c67d0893436bb27d"),
    mta=web3.toChecksumAddress("0xa3BeD4E1c75D00fa6f4E5E6922DB7261B5E9AcD2"),
    usdp=web3.toChecksumAddress("0x1456688345527bE1f37E9e627DA0837D6f08C925"),
    ibbtc=web3.toChecksumAddress("0xc4E15973E6fF2A35cC804c2CF9D2a1b817a8b40F"),
    dfd=web3.toChecksumAddress("0x20c36f062a31865bed8a5b1e512d9a1a20aa333a"),
    ausdc="0xBcca60bB61934080951369a648Fb03DF4F96263C",
    cvx="0x4e3FBD56CD56c3e72c1403e103b45Db9da5B9D2B",
    cvxCrv="0x62B9c7356A2Dc64a1969e19C23e4f579F9810Aa7",
    pnt="0x89Ab32156e46F46D02ade3FEcbe5Fc4243B9AAeD",
    bor="0x3c9d6c1C73b31c837832c72E04D3152f051fc1A9",
    wibBTC="0x8751d4196027d4e6da63716fa7786b5174f04c15",
    ibbtcCrv="0xFbdCA68601f835b27790D98bbb8eC7f05FDEaA9B",
    ustWhCrv="0xCEAF7747579696A2F0bb206a14210e3c9e6fB269",
    threePool = "0xbEbc44782C7dB0a1A60Cb6fe97d0b483032FF1C7",
)

whales = DotMap(
    badger=DotMap(
        whale="0x19d099670a21bC0a8211a89B84cEdF59AbB4377F",
        token="0x3472A5A71965499acd81997a54BBA8D852C6E53d",
    ),
    bBadger=DotMap(
        whale="0xa9429271a28F8543eFFfa136994c0839E7d7bF77",
        token="0x19D97D8fA813EE2f51aD4B4e04EA08bAf4DFfC28",
    ),
    harvestSuperSett=DotMap(
        whale="0xeD0B7f5d9F6286d00763b0FFCbA886D8f9d56d5e",
        token="0xAf5A1DECfa95BAF63E0084a35c62592B774A2A87",
    ),
    uniBadgerWbtc=DotMap(
        whale="0x235c9e24D3FB2FAFd58a2E49D454Fdcd2DBf7FF1",
        token="0xcD7989894bc033581532D2cd88Da5db0A4b12859",
    ),
    uniDiggWbtc=DotMap(
        whale="0xc17078fdd324cc473f8175dc5290fae5f2e84714",
        token="0xe86204c4eddd2f70ee00ead6805f917671f56c52",
    ),
    sbtcCrv=DotMap(
        whale="0x1f08863f246fe456f94579d1a2009108b574f509",
        token=curve_registry.pools.sbtcCrv.token,
    ),
    bSbtcCrv=DotMap(
        whale="0x10fc82867013fce1bd624fafc719bb92df3172fc",
        token="0xd04c48A53c111300aD41190D63681ed3dAd998eC",
    ),
    renCrv=DotMap(
        whale="0x647481c033a4a2e816175ce115a0804adf793891",
        token=curve_registry.pools.renCrv.token,
    ),
    bRenCrv=DotMap(
        whale="0x2296f174374508278dc12b806a7f27c87d53ca15",
        token="0x6dEf55d2e18486B9dDfaA075bc4e4EE0B28c1545",
    ),
    tbtcCrv=DotMap(
        whale="0xb65cef03b9b89f99517643226d76e286ee999e77",
        token=curve_registry.pools.tbtcCrv.token,
    ),
    bTbtcCrv=DotMap(
        whale="0x085a9340ff7692ab6703f17ab5ffc917b580a6fd",
        token="0xb9D076fDe463dbc9f915E5392F807315Bf940334",
    ),
    hbtcCrv=DotMap(
        whale="0x7a7a599d2384ed203cfea49721628aa851e0da16",
        token=curve_registry.pools.hbtcCrv.token,
    ),
    pbtcCrv=DotMap(
        whale="0x5a87e9a0a765fe5a69fa6492d3c7838dc1511805",
        token=curve_registry.pools.pbtcCrv.token,
    ),
    obtcCrv=DotMap(
        whale="0xe5447efebb597267d6afe9c53e0aeaba7e617fa8",
        token=curve_registry.pools.obtcCrv.token,
    ),
    bbtcCrv=DotMap(
        whale="0x1423b6609bd8194ed2a6cfae0c52ad41e68f0821",
        token=curve_registry.pools.bbtcCrv.token,
    ),
    wbtc=DotMap(
        whale="0xc11b1268c1a384e55c48c2391d8d480264a3a7f4",
        token="0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599",
    ),
    sushiBadgerWbtc=DotMap(
        whale="0xc2EdaD668740f1aA35E4D8f227fB8E17dcA888Cd",
        token="0x110492b31c59716AC47337E616804E3E3AdC0b4a",
    ),
    sushiDiggWbtc=DotMap(
        whale="0xd16fda96cb572da89e4e39b04b99d99a8e3071fb",
        token="0x110492b31c59716AC47337E616804E3E3AdC0b4a",
    ),
    sushiWbtcEth=DotMap(
        whale="0xc2EdaD668740f1aA35E4D8f227fB8E17dcA888Cd",
        token="0xCEfF51756c56CeFFCA006cD410B03FFC46dd3a58",
    ),
    bSushiWbtcEth=DotMap(
        whale="0x032c701886ad0317f0e58c8f4a570c6f9c0bbf4a",
        token="0x758A43EE2BFf8230eeb784879CdcFF4828F2544D",
    ),
    usdc=DotMap(
        whale="0xbe0eb53f46cd790cd13851d5eff43d12404d33e8",  # binance
        token="0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
    ),
    digg=DotMap(
        whale="0x4a8651F2edD68850B944AD93f2c67af817F39F62",
        token="0x798D1bE841a82a273720CE31c822C61a67a601C3",
    ),
    renbtc=DotMap(
        whale="0x35ffd6e268610e764ff6944d07760d0efe5e40e5",
        token="0xeb4c2781e4eba804ce9a9803c67d0893436bb27d",
    ),
    imbtc=DotMap(
        whale="0xfd3ca26e839bf75870d50613cc20d34a59975c3e",
        token="0x17d8cbb6bce8cee970a4027d1198f6700a7a6c24",
    ),
    fPmBtcHBtc=DotMap(
        whale="0xf65d53aa6e2e4a5f4f026e73cb3e22c22d75e35c",
        token="0x48c59199Da51B7E30Ea200a74Ea07974e62C4bA7",
    ),
    mta=DotMap(
        whale="0xd156122399690b387702d4095dc24a397bcc8af5",
        token="0xa3bed4e1c75d00fa6f4e5e6922db7261b5e9acd2",
    ),
    triCrypto=DotMap(
        whale="0x9f719e0bc35c46236b3f450852b526d84fed514b",
        token="0xcA3d75aC011BF5aD07a98d02f18225F9bD9A6BDF",
    ),
    triCrypto2=DotMap(
        whale="0xad2c3faa391930f81212f71b6a8a094fa0346e9d",
        token="0xc4AD29ba4B3c580e6D59105FFf484999997675Ff",
    ),
    cvx=DotMap(
        whale="0xdd5bc57bf90e6c6b341120e5b38fb6eda8e6481d",
        token="0x4e3fbd56cd56c3e72c1403e103b45db9da5b9d2b",
    ),
    cvxCrv=DotMap(
        whale="0x00f282c40b92bed05f1776cadf1c8b96b9fbaee3",
        token="0x62b9c7356a2dc64a1969e19c23e4f579f9810aa7",
    ),
)

registry = DotMap(
    curve=curve_registry,
    convex=convex_registry,
    tokens=tokens,
    whales=whales,
)
