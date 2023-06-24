from TsyvinskiPortfolios  import TsyvinskyPortfolios
from CryptoCompare import CryptoCompare
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
lower_limit = 0.025
upper_limit = 0.975

def winsorize_column(column):
            lower_quantile = column.quantile(lower_limit)
            upper_quantile = column.quantile(upper_limit)
            for i in range(1, len(column)):
                if column[i] < lower_quantile or column[i] > upper_quantile:
                    column[i] = column[i-1] if column[i-1] >= lower_quantile and column[i-1] <= upper_quantile else np.nan
            return column


port = TsyvinskyPortfolios(1000000,90000,0.075)

mkt = port.generate_market_portfolio_returns()
mom = port.generate_momentum_portfolio_returns()
size = port.generate_size_portfolio_returns()


mkt.to_csv("MktRets.csv")
size.to_csv("SizeRets.csv")
mom.to_csv("MomRets.csv")

mkt = pd.read_csv("MktRets.csv")
size = pd.read_csv("SizeRets.csv")
mom =  pd.read_csv("MomRets.csv")


winmkt = mkt.apply(winsorize_column)
winsize = size.apply(winsorize_column)
winmom = mom.apply(winsorize_column)

winmkt.to_csv("WinMktRets.csv")
winsize.to_csv("WinSizeRets.csv")
winmom.to_csv("WinMomRets.csv")



port.plotter(winmkt['0'],winsize['0'],winmom['0'])