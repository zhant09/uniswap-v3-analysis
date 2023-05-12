class EthPoolInfo:
    def __init__(self, pool_id):
        self.pool_id = pool_id
        self.current_tick = 0
        self.fee_tier = 0
        self.tick_spacing = 0
        self.token0 = ""
        self.token1 = ""
        self.decimals0 = 0
        self.decimals1 = 0

    @property
    def pool_id(self):
        return self.pool_id

    @pool_id.setter
    def pool_id(self, value):
        self.pool_id = value

    @property
    def current_tick(self):
        return self.current_tick

    @current_tick.setter
    def current_tick(self, value):
        self.current_tick = value

    @property
    def fee_tier(self):
        return self.fee_tier

    @fee_tier.setter
    def fee_tier(self, value):
        self.fee_tier = value

    @property
    def tick_spacing(self):
        return self.tick_spacing

    @tick_spacing.setter
    def tick_spacing(self, value):
        self.tick_spacing = value

    @property
    def token0(self):
        return self.token0

    @token0.setter
    def token0(self, value):
        self.token0 = value

    @property
    def token1(self):
        return self.token1

    @token1.setter
    def token1(self, value):
        self.token1 = value

    @property
    def decimals0(self):
        return self.decimals0

    @decimals0.setter
    def decimals0(self, value):
        self.decimals0 = value

    @property
    def decimals1(self):
        return self.decimals1

    @decimals1.setter
    def decimals1(self, value):
        self.decimals1 = value
