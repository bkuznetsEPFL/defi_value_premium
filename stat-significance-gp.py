import pandas as pd
import numpy as np
import statsmodels.api as sm

"""
    Class reporting the regression parameters of gp portfolio returns on the benchmark portfolios
"""

mom = pd.read_csv("WinMomRets.csv")
size = pd.read_csv("WinSizeRets.csv")
mkt = pd.read_csv("WinMktRets.csv")



mom = mom['0']
size = size['0']
mkt = mkt['0']


df_concatenated = pd.concat([mkt,size,mom], axis=1)

df_concatenated.columns = ['Market', 'Size', 'Momentum']
df_concatenated =df_concatenated.tail(500).reset_index(drop=True)

#Start on January first
gprets = pd.read_csv("win_gp_vw.csv")

gprets = gprets['0']

gprets = gprets.head(500)
gprets = gprets.reset_index(drop=True)







# Perform the regression
X = df_concatenated[['Market', 'Size', 'Momentum']]  # Independent variables
y = gprets  # Dependent variable

X = sm.add_constant(X)  # Add constant term to the independent variables
model = sm.OLS(y, X)  # Create the Ordinary Least Squares (OLS) model
results = model.fit()  # Fit the model

# Extract alpha and its significance
alpha = results.params['const']  # Extract the alpha coefficient
alpha_t_statistic = results.tvalues['const']
# Display the results
print("Daily Alpha:", alpha)
print("Daily Alpha significance (T-statistic):", alpha_t_statistic)