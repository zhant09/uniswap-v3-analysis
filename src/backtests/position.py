class Position(object):

    def __init__(self, init_eth, init_usd):
        self._init_eth = init_eth
        self._init_usd = init_usd
        self._current_eth = self._init_eth
        self._current_usd = self._init_usd

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
        self._current_eth += amount
        self._current_usd -= amount * price

    def sell(self, price, amount):
        self._current_eth -= amount
        self._current_usd += amount * price

    def get_init_value(self, price):
        return self._init_usd + self._init_eth * price

    def get_current_value(self, current_price):
        return self._current_usd + self._current_eth * current_price

    def get_profit(self, current_price):
        return self.get_current_value(current_price) - self.get_init_value(current_price)

    def get_profit_rate(self, current_price):
        return self.get_profit(current_price) / self.get_init_value(current_price)