// SPDX-License-Identifier: MIT
pragma solidity >=0.5.0 <0.8.0;

interface WETH {
    function deposit() external payable;

    function withdraw(uint256 wad) external;

    function balanceOf(address account) external view returns (uint256);

    function approve(address guy, uint wad) external returns (bool);

    event Deposit(address indexed dst, uint256 wad);
    event Withdrawal(address indexed src, uint256 wad);
}
