import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


lower_limit = 0.025
upper_limit = 0.975

def plotter(gpew,gpvw):
        """
        Function plotting the cumulative portfolio returns, using their returns (csv)
        """

        headers = ['GP EW Portfolio Returns']
        df_gpew = gpew.to_frame()
        df_gpew.columns = headers
        df_gpew = df_gpew.mask(df_gpew.eq('None')).dropna()
        df_gpew['date'] = pd.date_range(end= '25/05/2023', periods=len(df_gpew), freq='D')
        df_gpew.set_index(['date'],inplace=True)

        df_gpew['GP EW Portfolio Returns'] +=1
        df_gpew = df_gpew.cumprod()

        headers = ['GP VW Portfolio Returns']

        df_gpvw = gpvw.to_frame()
        df_gpvw.columns =  headers
        df_gpvw = df_gpvw.mask(df_gpvw.eq('None')).dropna()
        df_gpvw['date'] = pd.date_range(end= '25/05/2023', periods=len(df_gpvw), freq='D')
        df_gpvw.set_index(['date'],inplace=True)

        df_gpvw['GP VW Portfolio Returns'] +=1
        df_gpvw = df_gpvw.cumprod()

        # Create a figure and axis object
        fig, ax = plt.subplots(figsize=(10, 5))

        # Plot the Market Portfolio Returns
        df_gpew.plot(ax=ax)

        # Plot the Size Portfolio Returns
        df_gpvw.plot(ax=ax)

       

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


gpvw = pd.read_csv("gp_returns-vw.csv")      

#Start from January 2022
gpvw = gpvw.tail(515).reset_index(drop=True)

gpvwwin = gpvw.copy().apply(winsorize_column)

gpvwwin.to_csv("win_gp_vw.csv")

#Change to path of ew gp
gpew = pd.read_csv("gp_returns-vw.csv")
gpew = gpew.tail(515).reset_index(drop=True)
gpewwin = gpew.copy().apply(winsorize_column)

gpewwin.to_csv("win_gp_ew.csv")




plotter(gpewwin['0'],gpvwwin['0'])