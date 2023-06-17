from TsyvinskiPortfolios  import TsyvinskyPortfolios
from ValuePortfolio import ValuePortfolio
from CryptoCompare import CryptoCompare
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import warnings 
warnings.filterwarnings("ignore")


# cc = CryptoCompare()

# all_coins = cc.available_coin_list().json()
# all_coins = [s for s in all_coins.get('Data')]

#port = TsyvinskyPortfolios(1000000, 10000, 0.01)

port2 = ValuePortfolio()

# mkt = port.generate_market_portfolio_returns()
# mom = port.generate_momentum_portfolio_returns()
# size = port.generate_size_portfolio_returns()

chml = port2.generate_chml_portfolio_returns()
#gp = port2.generate_gp_portfolio_returns()
gp = 0


#port.plotter(mkt,size,mom)

port2.plotter(chml,gp) 
