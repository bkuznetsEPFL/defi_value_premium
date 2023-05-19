from TsyvinskiPortfolios import TsyvinskyPortfolios
from CryptoCompare import CryptoCompare

cc = CryptoCompare()

all_coins = cc.available_coin_list().json()
all_coins = [s for s in all_coins.get('Data')]

port = TsyvinskyPortfolios(1000000, 10000, 0.01)

mkt = port.generate_market_portfolio_returns()
mom = port.generate_momentum_portfolio_returns()
size = port.generate_size_portfolio_returns()

port.plotter(mkt, size, mom)
