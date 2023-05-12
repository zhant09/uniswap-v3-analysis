class EthPoolInfo:
    def __init__(self, pool_id):
        self._pool_id = pool_id
        self._current_tick = 0
        self._fee_tier = 0
        self._tick_spacing = 0
        self._token0 = ""
        self._token1 = ""
        self._decimals0 = 0
        self._decimals1 = 0

    @property
    def pool_id(self):
        return self._pool_id

    @pool_id.setter
    def pool_id(self, value):
        self._pool_id = value

    @property
    def current_tick(self):
        return self._current_tick

    @current_tick.setter
    def current_tick(self, value):
        self._current_tick = value

    @property
    def fee_tier(self):
        return self._fee_tier

    @fee_tier.setter
    def fee_tier(self, value):
        self._fee_tier = value

    @property
    def tick_spacing(self):
        return self._tick_spacing

    @tick_spacing.setter
    def tick_spacing(self, value):
        self._tick_spacing = value

    @property
    def token0(self):
        return self._token0

    @token0.setter
    def token0(self, value):
        self._token0 = value

    @property
    def token1(self):
        return self._token1

    @token1.setter
    def token1(self, value):
        self._token1 = value

    @property
    def decimals0(self):
        return self._decimals0

    @decimals0.setter
    def decimals0(self, value):
        self._decimals0 = value

    @property
    def decimals1(self):
        return self._decimals1

    @decimals1.setter
    def decimals1(self, value):
        self._decimals1 = value
