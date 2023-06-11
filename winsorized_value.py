import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


lower_limit = 0.025
upper_limit = 0.975

def plotter(gp,chml):
        """
        Function plotting the cumulative portfolio returns, using their returns (csv)
        """

        headers = ['GP Portfolio Returns']
        df_gp = gp.to_frame()
        df_gp.columns = headers
        # df_gp = df_gp.replace([np.inf, -np.inf], np.nan).dropna(axis=0)
        df_gp = df_gp.mask(df_gp.eq('None')).dropna()
        df_gp['date'] = pd.date_range(end= '07/06/2023', periods=len(df_gp), freq='D')
        df_gp.set_index(['date'],inplace=True)

        df_gp['GP Portfolio Returns'] +=1
        df_gp = df_gp.cumprod()

        headers = ['CHML Portfolio Returns']

        df_chml = chml.to_frame()
        df_chml.columns =  headers
        # df_chml = df_chml.replace([np.inf, -np.inf], np.nan).dropna(axis=0)
        df_chml = df_chml.mask(df_chml.eq('None')).dropna()
        df_chml['date'] = pd.date_range(end= '07/06/2023', periods=len(df_chml), freq='D')
        df_chml.set_index(['date'],inplace=True)

        df_chml['CHML Portfolio Returns'] +=1
        df_chml = df_chml.cumprod()

        # Create a figure and axis object
        fig, ax = plt.subplots(figsize=(10, 5))

        # Plot the Market Portfolio Returns
        df_gp.plot(ax=ax)

        # Plot the Size Portfolio Returns
        df_chml.plot(ax=ax)

       

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


gp = pd.read_csv("gp_returns.csv")      
gpwin = gp.apply(winsorize_column)

gpwin.to_csv("winsizerets.csv")


chml = pd.read_csv("chml_returns.csv")

chmlwin = chml.apply(winsorize_column)

chmlwin.to_csv("winmktrets.csv")




plotter(gpwin['0'],chmlwin['0'])