class Position(object):

    def __init__(self, init_eth, init_usd, trading_fee):
        self._init_eth = init_eth
        self._init_usd = init_usd
        self._current_eth = self._init_eth
        self._current_usd = self._init_usd
        self.trading_fee = trading_fee

    @property
    def init_eth(self):
        return self._init_eth

    @property
    def init_usd(self):
        return self._init_usd

    @property
    def current_eth(self):
        return self._current_eth

    @current_eth.setter
    def current_eth(self, value):
        self._current_eth = value

    @property
    def current_usd(self):
        return self._current_usd

    @current_usd.setter
    def current_usd(self, value):
        self._current_usd = value

    def buy(self, price, amount):
        if self._current_usd < amount * price * (1 + self.trading_fee):
            raise ValueError("not enough usd to buy")

        self._current_eth += amount
        self._current_usd -= amount * price * (1 + self.trading_fee)

    # consume the amount including trading fee
    def sell(self, price, amount):
        if self._current_eth < amount:
            raise ValueError("not enough eth to sell")

        self._current_eth -= amount
        self._current_usd += amount * (1 - self.trading_fee) * price

    def get_init_value(self, price):
        return self._init_usd + self._init_eth * price

    def get_value(self, current_price):
        return self._current_usd + self._current_eth * current_price

    def get_profit(self, current_price):
        return self.get_value(current_price) - self.get_init_value(current_price)

    def get_profit_rate(self, current_price):
        return self.get_profit(current_price) / self.get_init_value(current_price)

    def __str__(self):
        return "current_eth: {}, current_usd: {}".format(self.current_eth, self.current_usd)


class GeneralPosition(object):

    def __init__(self, token0, token1, token0_amount, token1_amount, trading_fee):
        self._token0 = token0
        self._token1 = token1
        self._init_token0_amount = token0_amount
        self._init_token1_amount = token1_amount
        self._current_token0_amount = self._init_token0_amount
        self._current_token1_amount = self._init_token1_amount
        self.trading_fee = trading_fee

    @property
    def token0(self):
        return self._token0

    @property
    def token1(self):
        return self._token1

    @property
    def init_token0_amount(self):
        return self._init_token0_amount

    @property
    def init_token1_amount(self):
        return self._init_token1_amount

    @property
    def current_token0_amount(self):
        return self._current_token0_amount

    @current_token0_amount.setter
    def current_token0_amount(self, value):
        self._current_token0_amount = value

    @property
    def current_token1_amount(self):
        return self._current_token1_amount

    @current_token1_amount.setter
    def current_token1_amount(self, value):
        self._current_token1_amount = value

    # price is token0 to token1 price
    def buy_token0(self, price, amount):
        if self._current_token1_amount < amount * price * (1 + self.trading_fee):
            raise ValueError("not enough token1 to buy token0")

        self._current_token0_amount += amount
        self._current_token1_amount -= amount * price * (1 + self.trading_fee)

    def sell_token0(self, price, amount):
        if self._current_token0_amount < amount:
            raise ValueError("not enough token0 to sell")

        self._current_token0_amount -= amount
        self._current_token1_amount += amount * (1 - self.trading_fee) * price

    def get_profit(self, price):
        return self._current_token1_amount + self._current_token0_amount * price - self._init_token1_amount - \
            self._init_token0_amount * price

    def get_profit_rate(self, price):
        return self.get_profit(price) / (self._init_token1_amount + self._init_token0_amount * price)
