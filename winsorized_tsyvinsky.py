import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


lower_limit = 0.025
upper_limit = 0.975

def plotter(market,size,momentum):
        """
        Function plotting the cumulative portfolio returns, using their returns (csv)
        """




        headers = ['Market Portfolio Returns']
        df_market = market.to_frame()
        df_market.columns = headers
        # df_market = df_market.replace([np.inf, -np.inf], np.nan).dropna(axis=0)
        df_market = df_market.mask(df_market.eq('None')).dropna()
        df_market['date'] = pd.date_range(end= '22/05/2023', periods=len(df_market), freq='D')
        df_market.set_index(['date'],inplace=True)

        df_market['Market Portfolio Returns'] +=1
        df_market = df_market.cumprod()

        headers = ['Size Portfolio Returns']

        df_size = size.to_frame()
        df_size.columns =  headers
        # df_size = df_size.replace([np.inf, -np.inf], np.nan).dropna(axis=0)
        df_size = df_size.mask(df_size.eq('None')).dropna()
        df_size['date'] = pd.date_range(end= '22/05/2023', periods=len(df_size), freq='D')
        df_size.set_index(['date'],inplace=True)

        df_size['Size Portfolio Returns'] +=1
        df_size = df_size.cumprod()


        headers2 = ['Momentum Portfolio Returns']

        df_mom = momentum.to_frame()
        df_mom.columns = headers2

        # df_mom = df_mom.replace([np.inf, -np.inf], np.nan).dropna(axis=0)
        df_mom = df_mom.mask(df_mom.eq('None')).dropna()


        df_mom['date'] = pd.date_range(end= '22/05/2023', periods=len(df_mom), freq='D')
        df_mom.set_index(['date'],inplace=True)


        df_mom['Momentum Portfolio Returns'] +=1
        df_mom = df_mom.cumprod()

        # Create a figure and axis object
        fig, ax = plt.subplots(figsize=(10, 5))

        # Plot the Market Portfolio Returns
        df_market.plot(ax=ax)

        # Plot the Size Portfolio Returns
        df_size.plot(ax=ax)

        # Plot the Momentum Portfolio Returns
        df_mom.plot(ax=ax)

        # Set the title and axis labels
        ax.set_title('Portfolio Returns')
        ax.set_xlabel('Date')
        ax.set_ylabel('Cumulative Returns')

        # Show the plot
        plt.show()

def winsorize_column(column):
            lower_quantile = column.quantile(lower_limit)
            upper_quantile = column.quantile(upper_limit)
            for i in range(1, len(column)):
                if column[i] < lower_quantile or column[i] > upper_quantile:
                    column[i] = column[i-1] if column[i-1] >= lower_quantile and column[i-1] <= upper_quantile else np.nan
            return column


size = pd.read_csv("-SizeRets.csv")

sizewin = size.apply(winsorize_column)

sizewin.to_csv("winsizerets.csv")


mkt = pd.read_csv("-MktRets.csv")

mktwin = mkt.apply(winsorize_column)

mktwin.to_csv("winmktrets.csv")


mom = pd.read_csv("-MomRets.csv")

momwin = mom.apply(winsorize_column)


momwin.to_csv("winmomrets.csv")



plotter(mktwin['0'],sizewin['0'],momwin['0'])
