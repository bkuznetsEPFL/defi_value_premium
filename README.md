# Value Premium in DeFi

### Introduction
The goal is to backtest the DeFi value strategy and test it
against the 3-factor crypto model proposed in L. Yukun, 
A. Tsyvinski and Wu Xi. For backtesting, we estimate bid-ask
spreads using the estimator of Shane A. Corwin, Paul Schultz
(https://doi.org/10.1111/j.1540-6261.2012.01729.x) or the
one from D. Ardia, E. Guidotti, and T. Kroencke (2022) or 
Roll (1984), all estimators use historical OHLC prices. 
Then, we estimate historical price impact using historical
volume data. Data are from CryptoCompare.com, enterprise
subscription.



### Tutorial:

To generate the Tsyvinski portfolio returns (Market, size, and momentum) you can run the main-Tsyvinski.py class

To generate the Value portfolio returns (GP and CHML) you can run the main-Value.py class (Note that the plots returns need to be windsorized, so you have to run winsorized_gp.py and winsorized_chml.py to generate the plots)

To regress GP on the Tsyvinski portfolios, run stat-significance-gp.py

To regress CHML on the Tsyvinski portfolios, run stat-significance-chml.py

Note that for the GP and CHML portfolios, if you need the respective EW portfolios you should uncoment the specified part of the code in the ValuePortfolio.py class

Quintiles.py Generates the quintile portfolios discussed in Tsyvinski, However we used it for testing purposes