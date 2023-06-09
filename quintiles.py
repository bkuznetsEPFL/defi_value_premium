

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

class TsyvinskyPortfolios:
    """
    Class constructing the quintiles portfolios as discussed
    in Y. Liu, A. Tsyvinski, Xi Wu, "Common Risk
    Factors in Cryptocurrency", pp. 20-21, see
    https://dx.doi.org/10.2139/ssrn.3379131
    """

    def __init__(self, all_symbols,mkcap_treshold,volume_treshold,min_price_treshold):
        


        # ohlcv = pd.read_csv('data/ohlcv_panel_USD_2000_CCCAGG_all.csv')
        # block = pd.read_csv('data/blockchain_panel_2000_all.csv')
        ohlcv = pd.read_csv('data/ohlcv_panel_USD2000CCCAGG_all.csv')
        block = pd.read_csv('data/blockchain_panel_2000_all.csv')
        


        supply_data = block.pivot(index = 'time', columns = 'symbol', values = 'current_supply')
        prices_data = ohlcv.pivot(index = 'time', columns = 'fsym', values = 'close')
        volumeto_data = ohlcv.pivot(index = 'time', columns = 'fsym', values = 'volumeto')
        volumefrom_data = ohlcv.pivot(index = 'time', columns = 'fsym', values = 'volumefrom') 

        dfprices = prices_data
        common_cols = dfprices.columns.intersection(supply_data.columns)
        common_cols = sorted(common_cols)
        
    

        self.mkcap = pd.DataFrame(columns= common_cols)
        self.dfvolume = pd.DataFrame(columns= common_cols)
        self.momt = pd.DataFrame(columns= common_cols)
        self.dfreturns = pd.DataFrame(columns= common_cols)
        dfprices = dfprices[common_cols].drop(dfprices.index[-1])
        dfprices = dfprices[np.abs(dfprices) > min_price_treshold]
        supply_data = supply_data[common_cols]
        volumeto_data = volumeto_data[common_cols].drop(volumeto_data.index[-1])
        volumefrom_data = volumefrom_data[common_cols].drop(volumefrom_data.index[-1])
        self.dfvolume = volumeto_data + volumefrom_data*dfprices
        self.mkcap = supply_data*dfprices  
        self.momt =    (dfprices - dfprices.shift(21))/dfprices.shift(21)
        self.dfreturns = (dfprices - dfprices.shift(1))/dfprices.shift(1)

        
        self.mkcap = self.mkcap.reset_index(drop=True)
        self.momt = self.momt.reset_index(drop=True)
        self.dfreturns = self.dfreturns.reset_index(drop=True)
        self.dfvolume = self.dfvolume.reset_index(drop=True)

        self.dfvolume.replace([np.inf, -np.inf], np.nan, inplace=True)
        self.dfreturns.replace([np.inf, -np.inf], np.nan, inplace=True)
        self.momt.replace([np.inf, -np.inf], np.nan, inplace=True)
        self.mkcap.replace([np.inf, -np.inf], np.nan, inplace=True)



        self.dfvolume = self.dfvolume.tail(3445).reset_index(drop=True)# 1 march 2014
        self.dfreturns = self.dfreturns.tail(3445).reset_index(drop=True)
        self.momt = self.momt.tail(3445).reset_index(drop=True)
        self.mkcap = self.mkcap.tail(3445).reset_index(drop=True)


        self.momentum_portfolio_positions = pd.DataFrame()
        self.market_portfolio_positions = pd.DataFrame()
        self.size_portfolio_positions = pd.DataFrame()

        lower_limit = 0.025
        upper_limit = 0.975


        self.returns_shifted = self.dfreturns.shift(-1)     

        return_cols = self.dfreturns.columns.tolist()


        self.rename_dict = dict(zip(common_cols, return_cols))

        self.generate_positions(mkcap_treshold,volume_treshold)

        self.momentum_portfolio_positions.to_csv("quintiles-MomentumPositions.csv")
        self.size_portfolio_positions.to_csv("quintiles-SizePositions.csv")
        self.market_portfolio_positions.to_csv("quintiles-MarketPositions.csv")
    def generate_positions(self,mkcap_treshhold,volume_treshold):

        """
        Function generating the positions of  the three  quintiles  portfolios as discussed
        in Y. Liu, A. Tsyvinski, Xi Wu, "Common Risk
        Factors in Cryptocurrency", pp. 20-21, see
        https://dx.doi.org/10.2139/ssrn.3379131
        """

        # Loop through each date in the momentum factor dataframe
        for index, row in self.momt.head(2400).iterrows():
          if index % 7 ==0 :
            print(index)
            # Create a new dataframe to store coin data for the current date
            data = pd.DataFrame(columns = ['Coin','Market-Cap','Momentum','VolumeTo'])


            # Get market cap and volume data for current date
            mkcap_r = self.mkcap.iloc[index]
            volume_r = self.dfvolume.iloc[index]
            ret = self.returns_shifted.iloc[index]

            # If data is available 21 days ago, get market cap, momentum, and volume data for that date
            if index > 21:
                data21 = pd.DataFrame(columns = ['Coin','Market-Cap','Momentum','VolumeTo'])
                mkcap21 = self.mkcap.iloc[index - 21]
                volume21 = self.dfvolume.iloc[index - 21]
                momentum21 = self.momt.iloc[index - 21]
                return21 = self.returns_shifted.iloc[index - 21]

            # Loop through each coin in the momentum factor dataframe
            for j,col in enumerate(self.momt.columns):
                # Create a new row with coin data
                new_row = {'Coin': col, 'Market-Cap':mkcap_r[j], 'Momentum': row[j],'VolumeTo': volume_r[j],'Retshifted': ret}
                # Append the new row to the data dataframe
                data = data.append(new_row, ignore_index = True)
                # If data is available 21 days ago, create a new row with coin data for that date and append it to the data21 dataframe
                if index > 21:
                    new_row21 = {'Coin': col, 'Market-Cap':mkcap21[j], 'Momentum': momentum21[j],'VolumeTo': volume21[j],'Retshifted': return21}
                    data21 = data21.append(new_row21, ignore_index = True)

            
            # Define a condition for removing coins from the portfolio
            condition  =  (data['Market-Cap'] < mkcap_treshhold) | (pd.isna(data['Market-Cap'])) | (data['VolumeTo'] < volume_treshold )| (pd.isna(data['VolumeTo']))



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


            #Size portfolio construction


            mdf = mdf.sort_values('Coin')
            weights = mdf['Weights'].T
            self.market_portfolio_positions = self.market_portfolio_positions.append(weights, ignore_index=False)
            data_sz = data[~condition]

            colmk = data_sz['Market-Cap']
            q1 = colmk.quantile(0.2)
            q2 = colmk.quantile(0.8)

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

            #Momentum Portfolio

            condition21 =  (data21['Market-Cap'] < mkcap_treshhold) | (pd.isna(data21['Market-Cap'])) | (data21['VolumeTo'] < volume_treshold )| (pd.isna(data21['VolumeTo']))     if index > 21 else False

            condition =  (data['Market-Cap'] < mkcap_treshhold) | (pd.isna(data['Market-Cap'])) | (data['VolumeTo'] < volume_treshold )| (pd.isna(data['VolumeTo'])) | (pd.isna(data['Momentum']))

            condition = condition | condition21

            data_mom = data[~condition]


            removed_data = data[condition]#Coins with market cap less than a million
            removed_data['Weights'] = np.nan



            data_mom = data_mom.sort_values(by = ['Market-Cap'],ascending= False)

            colmom = data_mom['Momentum']
            q1 = colmom.quantile(0.2)
            q2 = colmom.quantile(0.8)

            mom_up = data_mom.loc[colmom > q2]
            mom_middle = data_mom.loc[(q1 < colmom) & (colmom <= q2)]
            mom_down = data_mom.loc[colmom <= q1]

            
            mkcap_up = mom_up['Market-Cap']
            mkcap_middle = mom_middle['Market-Cap']
            mkcap_down = mom_down['Market-Cap']


            sum_up = sum(mkcap_up)
            sum_middle = sum(mkcap_middle)
            sum_down = sum(mkcap_down)


            weights_up = mkcap_up/sum_up
            weights_middle = mkcap_middle/sum_middle
            weights_down = mkcap_down/sum_down

            # Assign the weights to each coin based on size and momentum, multiplied by the investment strategy (sign)
            mom_up['Weights'] = 1*weights_up
            mom_middle['Weights'] = 0
            mom_down['Weights'] = -1*weights_down



            self.momentum_portfolio_positions  = self.momentum_portfolio_positions .reset_index(drop=True)


            #Reconcatenate all the coins, to be consistent with the columns of the data frame containing all dates
            momentum_conc = pd.concat([removed_data[['Coin','Weights']],mom_up[['Coin','Weights']],mom_middle[['Coin','Weights']],mom_down[['Coin','Weights']]])
            momentum_conc = momentum_conc.sort_values('Coin')

            momentum_conc['Coin'] = momentum_conc['Coin'].astype(str)


            weights = momentum_conc['Weights'].T


            
            self.momentum_portfolio_positions = self.momentum_portfolio_positions.append(weights, ignore_index=False)



    def generate_market_portfolio_returns(self):
        """
        Function generating  the market portfolio returns
        """
    
        self.market_portfolio_positions = self.market_portfolio_positions.rename(columns=self.rename_dict)
        rets_rep = pd.DataFrame(np.repeat(self.market_portfolio_positions.values, 7, axis=0), columns=self.market_portfolio_positions.columns)
        rets_rep.to_csv("quintiles-repeated_mkt.csv")
        self.market_portfolio_returns = rets_rep.mul(self.returns_shifted).sum(axis = 1)
        return self.market_portfolio_returns
    def generate_momentum_portfolio_returns(self):
        """
        Function generating  the momentum portfolio returns
        """
        self.momentum_portfolio_positions = self.momentum_portfolio_positions.rename(columns=self.rename_dict)
        rets_rep = pd.DataFrame(np.repeat(self.momentum_portfolio_positions.values, 7, axis=0), columns=self.momentum_portfolio_positions.columns)
        rets_rep.to_csv("quintiles-repeated_mom.csv")
        self.momentum_portfolio_returns = rets_rep.mul(self.returns_shifted).sum(axis = 1)
        return self.momentum_portfolio_returns 

    def generate_size_portfolio_returns(self):
        """
        Function generating  the size portfolio returns
        """
        self.size_portfolio_positions = self.size_portfolio_positions.rename(columns=self.rename_dict)
        rets_rep =pd.DataFrame(np.repeat(self.size_portfolio_positions.values, 7, axis=0), columns=self.size_portfolio_positions.columns)
        rets_rep.to_csv("quintiles-repeated_size.csv")
        self.size_portfolio_returns = rets_rep.mul(self.returns_shifted).sum(axis = 1)
        return self.size_portfolio_returns



    def plotter(self,market,size,momentum):
        """
        Function plotting the cumulative portfolio returns, using their returns (csv)
        """




        headers = ['Market Portfolio Returns']
        df_market = market.to_frame()
        df_market.columns = headers
        # df_market = df_market.replace([np.inf, -np.inf], np.nan).dropna(axis=0)
        df_market = df_market.mask(df_market.eq('None')).dropna()
        df_market['date'] = pd.date_range(end= '22/04/2023', periods=len(df_market), freq='D')
        df_market.set_index(['date'],inplace=True)

        df_market['Market Portfolio Returns'] +=1
        df_market = df_market.cumprod()

        headers = ['Size Portfolio Returns']

        df_size = size.to_frame()
        df_size.columns =  headers
        # df_size = df_size.replace([np.inf, -np.inf], np.nan).dropna(axis=0)
        df_size = df_size.mask(df_size.eq('None')).dropna()
        df_size['date'] = pd.date_range(end= '22/04/2023', periods=len(df_size), freq='D')
        df_size.set_index(['date'],inplace=True)

        df_size['Size Portfolio Returns'] +=1
        df_size = df_size.cumprod()


        headers2 = ['Momentum Portfolio Returns']

        df_mom = momentum.to_frame()
        df_mom.columns = headers2

        # df_mom = df_mom.replace([np.inf, -np.inf], np.nan).dropna(axis=0)
        df_mom = df_mom.mask(df_mom.eq('None')).dropna()


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