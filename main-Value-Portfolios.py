from ValuePortfolio import ValuePortfolio
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import warnings 
warnings.filterwarnings("ignore")

port2 = ValuePortfolio()

chml = port2.generate_chml_portfolio_returns()
gp = port2.generate_gp_portfolio_returns()


