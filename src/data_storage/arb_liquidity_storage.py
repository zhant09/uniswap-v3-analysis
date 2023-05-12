arb_daily_liquidity_query = """
{
    tickDailySnapshots(where: {pool: "0xc31e54c7a869b9fcbecc14363cf510d1c41fa443", day: 19478}) {
        day
        tick {
            index
            liquidityNet
        }
    }
}
"""
