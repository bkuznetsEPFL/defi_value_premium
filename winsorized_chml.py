import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


lower_limit = 0.025
upper_limit = 0.975

def plotter(chmlew,chmlvw):
        """
        Function plotting the cumulative portfolio returns, using their returns (csv)
        """

        headers = ['CHML EW Portfolio Returns']
        df_chmlew = chmlew.to_frame()
        df_chmlew.columns = headers
        # df_gp = df_gp.replace([np.inf, -np.inf], np.nan).dropna(axis=0)
        df_chmlew = df_chmlew.mask(df_chmlew.eq('None')).dropna()
        df_chmlew['date'] = pd.date_range(end= '25/05/2023', periods=len(df_chmlew), freq='D')
        df_chmlew.set_index(['date'],inplace=True)

        df_chmlew['CHML EW Portfolio Returns'] +=1
        df_chmlew = df_chmlew.cumprod()

        headers = ['CHML VW Portfolio Returns']

        df_chmlvw = chmlvw.to_frame()
        df_chmlvw.columns =  headers
        df_chmlvw = df_chmlvw.mask(df_chmlvw.eq('None')).dropna()
        df_chmlvw['date'] = pd.date_range(end= '25/05/2023', periods=len(df_chmlvw), freq='D')
        df_chmlvw.set_index(['date'],inplace=True)

        df_chmlvw['CHML VW Portfolio Returns'] +=1
        df_chmlvw = df_chmlvw.cumprod()

        # Create a figure and axis object
        fig, ax = plt.subplots(figsize=(10, 5))

        # Plot the Market Portfolio Returns
        df_chmlew.plot(ax=ax)

        # Plot the Size Portfolio Returns
        df_chmlvw.plot(ax=ax)

       

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


chmlvw = pd.read_csv("chml_returns-vw.csv")      

chmlvw = chmlvw.tail(815).reset_index(drop=True)

chmlvwwin = chmlvw.copy().apply(winsorize_column)

chmlvwwin.to_csv("win_chml_vw.csv")

#change to path of ew chml
chmlew = pd.read_csv("chml_returns-vw.csv")
chmlew = chmlew.tail(815).reset_index(drop=True)
chmlewwin = chmlew.copy().apply(winsorize_column)

chmlewwin.to_csv("win_chml_ew.csv")




plotter(chmlvwwin['0'],chmlvwwin['0'])