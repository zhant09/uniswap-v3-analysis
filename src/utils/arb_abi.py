arb_pool_abi = [{"inputs": [], "stateMutability": "nonpayable", "trade_type": "constructor"}, {"anonymous": False, "inputs": [{"indexed": True, "internalType": "address", "name": "owner", "trade_type": "address"}, {"indexed": True, "internalType": "int24", "name": "tickLower", "trade_type": "int24"}, {"indexed": True, "internalType": "int24", "name": "tickUpper", "trade_type": "int24"}, {"indexed": False, "internalType": "uint128", "name": "amount", "trade_type": "uint128"}, {"indexed": False, "internalType": "uint256", "name": "amount0", "trade_type": "uint256"}, {"indexed": False, "internalType": "uint256", "name": "amount1", "trade_type": "uint256"}], "name": "Burn", "trade_type": "event"}, {"anonymous": False, "inputs": [{"indexed": True, "internalType": "address", "name": "owner", "trade_type": "address"}, {"indexed": False, "internalType": "address", "name": "recipient", "trade_type": "address"}, {"indexed": True, "internalType": "int24", "name": "tickLower", "trade_type": "int24"}, {"indexed": True, "internalType": "int24", "name": "tickUpper", "trade_type": "int24"}, {"indexed": False, "internalType": "uint128", "name": "amount0", "trade_type": "uint128"}, {"indexed": False, "internalType": "uint128", "name": "amount1", "trade_type": "uint128"}], "name": "Collect", "trade_type": "event"}, {"anonymous": False, "inputs": [{"indexed": True, "internalType": "address", "name": "sender", "trade_type": "address"}, {"indexed": True, "internalType": "address", "name": "recipient", "trade_type": "address"}, {"indexed": False, "internalType": "uint128", "name": "amount0", "trade_type": "uint128"}, {"indexed": False, "internalType": "uint128", "name": "amount1", "trade_type": "uint128"}], "name": "CollectProtocol", "trade_type": "event"}, {"anonymous": False, "inputs": [{"indexed": True, "internalType": "address", "name": "sender", "trade_type": "address"}, {"indexed": True, "internalType": "address", "name": "recipient", "trade_type": "address"}, {"indexed": False, "internalType": "uint256", "name": "amount0", "trade_type": "uint256"}, {"indexed": False, "internalType": "uint256", "name": "amount1", "trade_type": "uint256"}, {"indexed": False, "internalType": "uint256", "name": "paid0", "trade_type": "uint256"}, {"indexed": False, "internalType": "uint256", "name": "paid1", "trade_type": "uint256"}], "name": "Flash", "trade_type": "event"}, {"anonymous": False, "inputs": [{"indexed": False, "internalType": "uint16", "name": "observationCardinalityNextOld", "trade_type": "uint16"}, {"indexed": False, "internalType": "uint16", "name": "observationCardinalityNextNew", "trade_type": "uint16"}], "name": "IncreaseObservationCardinalityNext", "trade_type": "event"}, {"anonymous": False, "inputs": [{"indexed": False, "internalType": "uint160", "name": "sqrtPriceX96", "trade_type": "uint160"}, {"indexed": False, "internalType": "int24", "name": "tick", "trade_type": "int24"}], "name": "Initialize", "trade_type": "event"}, {"anonymous": False, "inputs": [{"indexed": False, "internalType": "address", "name": "sender", "trade_type": "address"}, {"indexed": True, "internalType": "address", "name": "owner", "trade_type": "address"}, {"indexed": True, "internalType": "int24", "name": "tickLower", "trade_type": "int24"}, {"indexed": True, "internalType": "int24", "name": "tickUpper", "trade_type": "int24"}, {"indexed": False, "internalType": "uint128", "name": "amount", "trade_type": "uint128"}, {"indexed": False, "internalType": "uint256", "name": "amount0", "trade_type": "uint256"}, {"indexed": False, "internalType": "uint256", "name": "amount1", "trade_type": "uint256"}], "name": "Mint", "trade_type": "event"}, {"anonymous": False, "inputs": [{"indexed": False, "internalType": "uint8", "name": "feeProtocol0Old", "trade_type": "uint8"}, {"indexed": False, "internalType": "uint8", "name": "feeProtocol1Old", "trade_type": "uint8"}, {"indexed": False, "internalType": "uint8", "name": "feeProtocol0New", "trade_type": "uint8"}, {"indexed": False, "internalType": "uint8", "name": "feeProtocol1New", "trade_type": "uint8"}], "name": "SetFeeProtocol", "trade_type": "event"}, {"anonymous": False, "inputs": [{"indexed": True, "internalType": "address", "name": "sender", "trade_type": "address"}, {"indexed": True, "internalType": "address", "name": "recipient", "trade_type": "address"}, {"indexed": False, "internalType": "int256", "name": "amount0", "trade_type": "int256"}, {"indexed": False, "internalType": "int256", "name": "amount1", "trade_type": "int256"}, {"indexed": False, "internalType": "uint160", "name": "sqrtPriceX96", "trade_type": "uint160"}, {"indexed": False, "internalType": "uint128", "name": "liquidity", "trade_type": "uint128"}, {"indexed": False, "internalType": "int24", "name": "tick", "trade_type": "int24"}], "name": "Swap", "trade_type": "event"}, {"inputs": [{"internalType": "int24", "name": "tickLower", "trade_type": "int24"}, {"internalType": "int24", "name": "tickUpper", "trade_type": "int24"}, {"internalType": "uint128", "name": "amount", "trade_type": "uint128"}], "name": "burn", "outputs": [{"internalType": "uint256", "name": "amount0", "trade_type": "uint256"}, {"internalType": "uint256", "name": "amount1", "trade_type": "uint256"}], "stateMutability": "nonpayable", "trade_type": "function"}, {"inputs": [{"internalType": "address", "name": "recipient", "trade_type": "address"}, {"internalType": "int24", "name": "tickLower", "trade_type": "int24"}, {"internalType": "int24", "name": "tickUpper", "trade_type": "int24"}, {"internalType": "uint128", "name": "amount0Requested", "trade_type": "uint128"}, {"internalType": "uint128", "name": "amount1Requested", "trade_type": "uint128"}], "name": "collect", "outputs": [{"internalType": "uint128", "name": "amount0", "trade_type": "uint128"}, {"internalType": "uint128", "name": "amount1", "trade_type": "uint128"}], "stateMutability": "nonpayable", "trade_type": "function"}, {"inputs": [{"internalType": "address", "name": "recipient", "trade_type": "address"}, {"internalType": "uint128", "name": "amount0Requested", "trade_type": "uint128"}, {"internalType": "uint128", "name": "amount1Requested", "trade_type": "uint128"}], "name": "collectProtocol", "outputs": [{"internalType": "uint128", "name": "amount0", "trade_type": "uint128"}, {"internalType": "uint128", "name": "amount1", "trade_type": "uint128"}], "stateMutability": "nonpayable", "trade_type": "function"}, {"inputs": [], "name": "factory", "outputs": [{"internalType": "address", "name": "", "trade_type": "address"}], "stateMutability": "view", "trade_type": "function"}, {"inputs": [], "name": "fee", "outputs": [{"internalType": "uint24", "name": "", "trade_type": "uint24"}], "stateMutability": "view", "trade_type": "function"}, {"inputs": [], "name": "feeGrowthGlobal0X128", "outputs": [{"internalType": "uint256", "name": "", "trade_type": "uint256"}], "stateMutability": "view", "trade_type": "function"}, {"inputs": [], "name": "feeGrowthGlobal1X128", "outputs": [{"internalType": "uint256", "name": "", "trade_type": "uint256"}], "stateMutability": "view", "trade_type": "function"}, {"inputs": [{"internalType": "address", "name": "recipient", "trade_type": "address"}, {"internalType": "uint256", "name": "amount0", "trade_type": "uint256"}, {"internalType": "uint256", "name": "amount1", "trade_type": "uint256"}, {"internalType": "bytes", "name": "data", "trade_type": "bytes"}], "name": "flash", "outputs": [], "stateMutability": "nonpayable", "trade_type": "function"}, {"inputs": [{"internalType": "uint16", "name": "observationCardinalityNext", "trade_type": "uint16"}], "name": "increaseObservationCardinalityNext", "outputs": [], "stateMutability": "nonpayable", "trade_type": "function"}, {"inputs": [{"internalType": "uint160", "name": "sqrtPriceX96", "trade_type": "uint160"}], "name": "initialize", "outputs": [], "stateMutability": "nonpayable", "trade_type": "function"}, {"inputs": [], "name": "liquidity", "outputs": [{"internalType": "uint128", "name": "", "trade_type": "uint128"}], "stateMutability": "view", "trade_type": "function"}, {"inputs": [], "name": "maxLiquidityPerTick", "outputs": [{"internalType": "uint128", "name": "", "trade_type": "uint128"}], "stateMutability": "view", "trade_type": "function"}, {"inputs": [{"internalType": "address", "name": "recipient", "trade_type": "address"}, {"internalType": "int24", "name": "tickLower", "trade_type": "int24"}, {"internalType": "int24", "name": "tickUpper", "trade_type": "int24"}, {"internalType": "uint128", "name": "amount", "trade_type": "uint128"}, {"internalType": "bytes", "name": "data", "trade_type": "bytes"}], "name": "mint", "outputs": [{"internalType": "uint256", "name": "amount0", "trade_type": "uint256"}, {"internalType": "uint256", "name": "amount1", "trade_type": "uint256"}], "stateMutability": "nonpayable", "trade_type": "function"}, {"inputs": [{"internalType": "uint256", "name": "", "trade_type": "uint256"}], "name": "observations", "outputs": [{"internalType": "uint32", "name": "blockTimestamp", "trade_type": "uint32"}, {"internalType": "int56", "name": "tickCumulative", "trade_type": "int56"}, {"internalType": "uint160", "name": "secondsPerLiquidityCumulativeX128", "trade_type": "uint160"}, {"internalType": "bool", "name": "initialized", "trade_type": "bool"}], "stateMutability": "view", "trade_type": "function"}, {"inputs": [{"internalType": "uint32[]", "name": "secondsAgos", "trade_type": "uint32[]"}], "name": "observe", "outputs": [{"internalType": "int56[]", "name": "tickCumulatives", "trade_type": "int56[]"}, {"internalType": "uint160[]", "name": "secondsPerLiquidityCumulativeX128s", "trade_type": "uint160[]"}], "stateMutability": "view", "trade_type": "function"}, {"inputs": [{"internalType": "bytes32", "name": "", "trade_type": "bytes32"}], "name": "positions", "outputs": [{"internalType": "uint128", "name": "liquidity", "trade_type": "uint128"}, {"internalType": "uint256", "name": "feeGrowthInside0LastX128", "trade_type": "uint256"}, {"internalType": "uint256", "name": "feeGrowthInside1LastX128", "trade_type": "uint256"}, {"internalType": "uint128", "name": "tokensOwed0", "trade_type": "uint128"}, {"internalType": "uint128", "name": "tokensOwed1", "trade_type": "uint128"}], "stateMutability": "view", "trade_type": "function"}, {"inputs": [], "name": "protocolFees", "outputs": [{"internalType": "uint128", "name": "token0", "trade_type": "uint128"}, {"internalType": "uint128", "name": "token1", "trade_type": "uint128"}], "stateMutability": "view", "trade_type": "function"}, {"inputs": [{"internalType": "uint8", "name": "feeProtocol0", "trade_type": "uint8"}, {"internalType": "uint8", "name": "feeProtocol1", "trade_type": "uint8"}], "name": "setFeeProtocol", "outputs": [], "stateMutability": "nonpayable", "trade_type": "function"}, {"inputs": [], "name": "slot0", "outputs": [{"internalType": "uint160", "name": "sqrtPriceX96", "trade_type": "uint160"}, {"internalType": "int24", "name": "tick", "trade_type": "int24"}, {"internalType": "uint16", "name": "observationIndex", "trade_type": "uint16"}, {"internalType": "uint16", "name": "observationCardinality", "trade_type": "uint16"}, {"internalType": "uint16", "name": "observationCardinalityNext", "trade_type": "uint16"}, {"internalType": "uint8", "name": "feeProtocol", "trade_type": "uint8"}, {"internalType": "bool", "name": "unlocked", "trade_type": "bool"}], "stateMutability": "view", "trade_type": "function"}, {"inputs": [{"internalType": "int24", "name": "tickLower", "trade_type": "int24"}, {"internalType": "int24", "name": "tickUpper", "trade_type": "int24"}], "name": "snapshotCumulativesInside", "outputs": [{"internalType": "int56", "name": "tickCumulativeInside", "trade_type": "int56"}, {"internalType": "uint160", "name": "secondsPerLiquidityInsideX128", "trade_type": "uint160"}, {"internalType": "uint32", "name": "secondsInside", "trade_type": "uint32"}], "stateMutability": "view", "trade_type": "function"}, {"inputs": [{"internalType": "address", "name": "recipient", "trade_type": "address"}, {"internalType": "bool", "name": "zeroForOne", "trade_type": "bool"}, {"internalType": "int256", "name": "amountSpecified", "trade_type": "int256"}, {"internalType": "uint160", "name": "sqrtPriceLimitX96", "trade_type": "uint160"}, {"internalType": "bytes", "name": "data", "trade_type": "bytes"}], "name": "swap", "outputs": [{"internalType": "int256", "name": "amount0", "trade_type": "int256"}, {"internalType": "int256", "name": "amount1", "trade_type": "int256"}], "stateMutability": "nonpayable", "trade_type": "function"}, {"inputs": [{"internalType": "int16", "name": "", "trade_type": "int16"}], "name": "tickBitmap", "outputs": [{"internalType": "uint256", "name": "", "trade_type": "uint256"}], "stateMutability": "view", "trade_type": "function"}, {"inputs": [], "name": "tickSpacing", "outputs": [{"internalType": "int24", "name": "", "trade_type": "int24"}], "stateMutability": "view", "trade_type": "function"}, {"inputs": [{"internalType": "int24", "name": "", "trade_type": "int24"}], "name": "ticks", "outputs": [{"internalType": "uint128", "name": "liquidityGross", "trade_type": "uint128"}, {"internalType": "int128", "name": "liquidityNet", "trade_type": "int128"}, {"internalType": "uint256", "name": "feeGrowthOutside0X128", "trade_type": "uint256"}, {"internalType": "uint256", "name": "feeGrowthOutside1X128", "trade_type": "uint256"}, {"internalType": "int56", "name": "tickCumulativeOutside", "trade_type": "int56"}, {"internalType": "uint160", "name": "secondsPerLiquidityOutsideX128", "trade_type": "uint160"}, {"internalType": "uint32", "name": "secondsOutside", "trade_type": "uint32"}, {"internalType": "bool", "name": "initialized", "trade_type": "bool"}], "stateMutability": "view", "trade_type": "function"}, {"inputs": [], "name": "token0", "outputs": [{"internalType": "address", "name": "", "trade_type": "address"}], "stateMutability": "view", "trade_type": "function"}, {"inputs": [], "name": "token1", "outputs": [{"internalType": "address", "name": "", "trade_type": "address"}], "stateMutability": "view", "trade_type": "function"}]