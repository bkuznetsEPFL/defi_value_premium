import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

class TsyvinskyPortfolios:
    """
    Class constructing the three  factor portfolios as discussed
    in Y. Liu, A. Tsyvinski, Xi Wu, "Common Risk
    Factors in Cryptocurrency", pp. 20-21, see
    https://dx.doi.org/10.2139/ssrn.3379131
    """

    def __init__(self, all_symbols,mkcap_treshold,volume_treshold,min_price_treshold):
        self.mkcap = pd.DataFrame(columns= all_symbols)
        self.dfvolume = pd.DataFrame(columns= all_symbols)
        self.momt = pd.DataFrame(columns= all_symbols)
        self.dfreturns = pd.DataFrame(columns= all_symbols)


        ohlcv = pd.read_csv('data/ohlcv_panel_USD_200_CCCAGG_all.csv')
        block = pd.read_csv('data/blockchain_panel_200_all.csv')

        for coin in all_symbols:
            prices = ohlcv[ohlcv['fsym'] == coin]['close'][1:].reset_index(drop=True)
            supply = block[block['symbol'] == coin]['current_supply'].reset_index(drop=True)
            vol_from = ohlcv[ohlcv['fsym'] == coin]['volumefrom'][1:].reset_index(drop=True)
            vol_to = ohlcv[ohlcv['fsym'] == coin]['volumeto'][1:].reset_index(drop=True)
            prices = prices[prices > min_price_treshold]
            # if (len(vol_from)==len(prices)):
            self.dfvolume[coin] = vol_to + vol_from*prices
            # if (len(prices)==len(supply)):
            self.mkcap[coin] = supply*prices
            prices  = prices.to_frame()
            
            self.momt[coin] = (prices - prices.shift(21))/prices.shift(21)
            self.dfreturns[coin] = (prices - prices.shift(1))/prices.shift(1)

        self.momentum_portfolio_positions = pd.DataFrame()
        self.market_portfolio_positions = pd.DataFrame()
        self.size_portfolio_positions = pd.DataFrame()

        self.returns_shifted = self.dfreturns.shift(-1)     
        print("MOMT")
        print(self.momt)
        print("dfret")
        print(self.dfreturns)
        print("vol")
        print(self.dfvolume)
        print(self.mkcap)

        return_cols = self.dfreturns.columns.tolist()


        self.rename_dict = dict(zip(all_symbols, return_cols))

        self.generate_positions(mkcap_treshold,volume_treshold)

    def generate_positions(self,mkcap_treshhold,volume_treshold):

        """
        Function generating the positions of  the three  factor portfolios as discussed
        in Y. Liu, A. Tsyvinski, Xi Wu, "Common Risk
        Factors in Cryptocurrency", pp. 20-21, see
        https://dx.doi.org/10.2139/ssrn.3379131
        """

        # Loop through each date in the momentum factor dataframe
        for index, row in self.momt.iterrows():
            print(index)
            # Create a new dataframe to store coin data for the current date
            data = pd.DataFrame(columns = ['Coin','Market-Cap','Momentum','VolumeTo'])


            # Get market cap and volume data for current date
            mkcap_r = self.mkcap.iloc[index]
            volume_r = self.dfvolume.iloc[index]


            # If data is available 21 days ago, get market cap, momentum, and volume data for that date
            if index > 21:
                data21 = pd.DataFrame(columns = ['Coin','Market-Cap','Momentum','VolumeTo'])
                mkcap21 = self.mkcap.iloc[index - 21]
                volume21 = self.dfvolume.iloc[index - 21]
                momentum21 = self.momt.iloc[index - 21]


            # Loop through each coin in the momentum factor dataframe
            for j,col in enumerate(self.momt.columns):
                # Create a new row with coin data
                new_row = {'Coin': col, 'Market-Cap':mkcap_r[j], 'Momentum': row[j],'VolumeTo': volume_r[j]}
                # Append the new row to the data dataframe
                data = data.append(new_row, ignore_index = True)
                # If data is available 21 days ago, create a new row with coin data for that date and append it to the data21 dataframe
                if index > 21:
                    new_row21 = {'Coin': col, 'Market-Cap':mkcap21[j], 'Momentum': momentum21[j],'VolumeTo': volume21[j]}
                    data21 = data21.append(new_row21, ignore_index = True)

            
            # Define a condition for removing coins from the portfolio
            condition  = (data['Market-Cap'] < mkcap_treshhold) | (pd.isna(data['Market-Cap'])) | (data['VolumeTo'] < volume_treshold )| (pd.isna(data['VolumeTo']))



            # Remove coins that meet the condition and store them in the removed_data dataframe
            removed_data = data[condition]
            removed_data['Weights'] = np.nan
            # Keep coins that meet the inverse condition in  the data dataframe
            data_mk = data[~condition]
            # Sort the remaining coins in the data dataframe by market cap in descending order
            data_mk = data_mk.sort_values(by = ['Market-Cap'],ascending= False)



            # Calculate the weights of each coin in the market portfolio based on market cap

            sum_mkcap = sum(data_mk['Market-Cap'])
            data_mk['Weights'] = data_mk['Market-Cap']/sum_mkcap

            data_mk = data_mk.sort_values('Coin')

            data_mk['Coin'] = data_mk['Coin'].astype(str)

            # Concatenate the market portfolio with the weights of all coins, and reset the index
            mdf = pd.concat([removed_data[['Coin','Weights']],data_mk[['Coin','Weights']]])

            self.market_portfolio_positions  = self.market_portfolio_positions.reset_index(drop=True)


            return_cols = self.dfreturns.columns.tolist()
            #dictionnary of column names
            self.rename_dict = dict(zip(self.market_portfolio_positions.columns.tolist(), return_cols))

            # self.market_portfolio_positions= self.market_portfolio_positions.rename(columns=rename_dict)

            #Size portfolio construction

            # Split the coins into three size groups based on market cap, and calculate the weights of each group

            mdf = mdf.sort_values('Coin')
            weights = mdf['Weights'].T
            self.market_portfolio_positions = self.market_portfolio_positions.append(weights, ignore_index=False)

            data_sz = data[~condition]

            colmk = data_sz['Market-Cap']
            q1 = colmk.quantile(0.3)
            q2 = colmk.quantile(0.7)

            data_up = data_sz.loc[colmk > q2]
            data_middle = data_sz.loc[(q1 < colmk) & (colmk <= q2)]
            data_down = data_sz.loc[colmk <= q1]

            mkcap_up = data_up['Market-Cap']
            mkcap_middle = data_middle['Market-Cap']
            mkcap_down = data_down['Market-Cap']


            sum_up = sum(mkcap_up)
            sum_middle = sum(mkcap_middle)
            sum_down = sum(mkcap_down)


            weights_up = mkcap_up/sum_up
            weights_middle = mkcap_middle/sum_middle
            weights_down = mkcap_down/sum_down

            # Assign the weights to each coin based on size and momentum, multiplied by the investment strategy (sign)
            data_up['Weights'] = -1*weights_up
            data_middle['Weights'] = 0
            data_down['Weights'] = weights_down

            # Concatenate the size portfolio with the weights of all coins
            size_p = pd.concat([removed_data[['Coin','Weights']],data_up[['Coin','Weights']],data_middle[['Coin','Weights']],data_down[['Coin','Weights']]])


            size_p['Coin'] = size_p['Coin'].astype(str)
            size_p = size_p.sort_values('Coin')

            self.size_portfolio_positions = self.size_portfolio_positions.reset_index(drop=True)
            weights = size_p['Weights'].T

            self.size_portfolio_positions = self.size_portfolio_positions.append(weights, ignore_index=False)

            # self.size_portfolio_positions= self.size_portfolio_positions.rename(columns=rename_dict)
            #Momentum Portfolio

            condition21 = (data21['Market-Cap'] < mkcap_treshhold) | (pd.isna(data21['Market-Cap'])) | (data21['VolumeTo'] < volume_treshold )| (pd.isna(data21['VolumeTo']))     if index > 21 else False
            condition = (data['Market-Cap'] < mkcap_treshhold) | (pd.isna(data['Market-Cap'])) | (data['VolumeTo'] < volume_treshold )| (pd.isna(data['VolumeTo'])) | (pd.isna(data['Momentum']))
            condition = condition | condition21

            data_mom = data[~condition]


            removed_data = data[condition]#Coins with market cap less than a million
            removed_data['Weights'] = np.nan



            data_mom = data_mom.sort_values(by = ['Market-Cap'],ascending= False)


            # Split data into two groups - those with market capitalization above the 50th percentile and those with market capitalization below or equal to the 50th percentile.
            colmk = data_mom['Market-Cap']
            small = data_mom.loc[colmk <= colmk.quantile(0.5)]
            big = data_mom.loc[colmk > colmk.quantile(0.5)]

            # For the big group, split into three subgroups based on momentum -
            # those with momentum above the 70th percentile, those with momentum between the 30th and 70th percentile,
            #  and those with momentum below or equal to the 30th percentile.

            colmom = big['Momentum']
            q1 = colmom.quantile(0.3)
            q2 = colmom.quantile(0.7)
            big_up = big.loc[colmom > q2]
            big_middle = big.loc[(q1 < colmom) & (colmom <= q2)]
            big_down = big.loc[colmom <= q1]

            biguplen =  len(big_up['Market-Cap']) 
            bigdownlen  = len(big_down['Market-Cap']) 
            # Calculate weights based on market capitalization and assign a value of 1 for the subgroup with the highest momentum,
            #  0 for the subgroup with medium momentum, and -1 for the subgroup with the lowest momentum.
            #  Multiply weights with the investment strategy sign for each subgroup.
            big_up['Weights'] = 1/biguplen if ((index > 21) & ((biguplen !=0) & (bigdownlen != 0))) else 0#LONG
            big_middle['Weights'] = 0
            big_down['Weights'] = -1*1/bigdownlen if ((index > 21) & ((biguplen !=0) & (bigdownlen != 0))) else 0#SHORT  
            
            # For the small group, split into three subgroups based on momentum - 
            # those with momentum above the 70th percentile, those with momentum between the 30th and 70th percentile, 
            # and those with momentum below or equal to the 30th percentile.           

            colmom = small['Momentum']
            q1 = colmom.quantile(0.3)
            q2 = colmom.quantile(0.7)
            small_up = small.loc[colmom > q2]
            small_middle = small.loc[(q1 < colmom) & (colmom <= q2)]
            small_down = small.loc[colmom <= q1]


            # Calculate weights based on market capitalization and assign a value of 1 for the subgroup with the highest momentum,
            #  0 for the subgroup with medium momentum, and -1 for the subgroup with the lowest momentum. 
            # Multiply weights with the investment strategy sign for each subgroup.

            smalluplen = len(small_up['Market-Cap']) 
            smalldownlen = len(small_down['Market-Cap'])
            small_up['Weights'] =  1/smalluplen if ((index > 21) & ((smalluplen !=0) & (smalldownlen != 0))) else 0#LONG
            small_middle['Weights'] = 0
            small_down['Weights'] = -1*1/smalldownlen if ((index > 21) & ((smalluplen !=0) & (smalldownlen != 0))) else 0#SHORT


            self.momentum_portfolio_positions  = self.momentum_portfolio_positions .reset_index(drop=True)


            #Reconcatenate all the coins, to be consistent with the columns of the data frame containing all dates
            momentum_conc = pd.concat([removed_data[['Coin','Weights']],big_up[['Coin','Weights']],big_middle[['Coin','Weights']],big_down[['Coin','Weights']],small_up[['Coin','Weights']],small_middle[['Coin','Weights']],small_down[['Coin','Weights']]])
            momentum_conc = momentum_conc.sort_values('Coin')

            momentum_conc['Coin'] = momentum_conc['Coin'].astype(str)


            weights = momentum_conc['Weights'].T


            
            self.momentum_portfolio_positions = self.momentum_portfolio_positions.append(weights, ignore_index=False)

            # self.momentum_portfolio_positions= self.momentum_portfolio_positions.rename(columns=rename_dict)


    def generate_market_portfolio_returns(self):
        """
        Function generating  the market portfolio returns
        """

        self.market_portfolio_positions = self.market_portfolio_positions.rename(columns=self.rename_dict)
        self.market_portfolio_returns = self.market_portfolio_positions.mul(self.returns_shifted).sum(axis = 1)
        return self.market_portfolio_returns
    def generate_momentum_portfolio_returns(self):
        """
        Function generating  the momentum portfolio returns
        """
        self.momentum_portfolio_positions = self.momentum_portfolio_positions.rename(columns=self.rename_dict)
        self.momentum_portfolio_returns = self.momentum_portfolio_positions.mul(self.returns_shifted).sum(axis = 1)
        return self.momentum_portfolio_returns 

    def generate_size_portfolio_returns(self):
        """
        Function generating  the size portfolio returns
        """
        self.size_portfolio_positions = self.size_portfolio_positions.rename(columns=self.rename_dict)
        self.size_portfolio_returns = self.size_portfolio_positions.mul(self.returns_shifted).sum(axis = 1)
        return self.size_portfolio_returns



    def plotter(self,market,size,momentum):
        """
        Function plotting the cumulative portfolio returns, using their returns (csv)
        """




        headers = ['Market Portfolio Returns']
        df_market = market.to_frame()
        df_market.columns = headers
        # df_market = df_market.replace([np.inf, -np.inf], np.nan).dropna(axis=0)
        # df_market = df_market.mask(df_market.eq('None')).dropna()
        df_market['date'] = pd.date_range(end= '22/04/2023', periods=len(df_market), freq='D')
        df_market.set_index(['date'],inplace=True)

        df_market['Market Portfolio Returns'] +=1
        df_market = df_market.cumprod()

        headers = ['Size Portfolio Returns']

        df_size = size.to_frame()
        df_size.columns =  headers
        df_size = df_size.replace([np.inf, -np.inf], np.nan).dropna(axis=0)
        df_size = df_size.mask(df_size.eq('None')).dropna()
        df_size['date'] = pd.date_range(end= '22/04/2023', periods=len(df_size), freq='D')
        df_size.set_index(['date'],inplace=True)

        df_size['Size Portfolio Returns'] +=1
        df_size = df_size.cumprod()


        headers2 = ['Momentum Portfolio Returns']

        df_mom = momentum.to_frame()
        df_mom.columns = headers2
        # df_mom = df_mom.replace([np.inf, -np.inf], np.nan).dropna(axis=0)
        # df_mom = df_mom.mask(df_mom.eq('None')).dropna()

        df_mom['date'] = pd.date_range(end= '22/04/2023', periods=len(df_mom), freq='D')
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