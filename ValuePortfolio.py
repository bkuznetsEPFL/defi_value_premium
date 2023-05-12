import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


class ValuePortfolio:

    def __init__ (self):

        tvls = pd.read_csv('data/tvls.csv')
        fees = pd.read_csv('data/fees.csv')
        mcaps = pd.read_csv('data/mcaps.csv')


        tvls = tvls.set_index('date')
        fees = fees.set_index('date')
        mcaps = mcaps.set_index('date')

        

        self.tvls = tvls
        self.fees = fees
        self.mcaps = mcaps

        self.tvls = self.tvls.replace(0, np.nan)
        self.fees = self.fees.replace(0, np.nan)
        self.mcaps = self.mcaps.replace(0, np.nan)  

        self.chml = self.tvls / self.mcaps
        self.gp = self.fees / self.tvls  

        self.chml_positions = pd.DataFrame()
        self.gp_positions = pd.DataFrame()


        self.dfreturns = (self.tvls - self.tvls.shift(1))/self.tvls.shift(1)

        self.returns_shifted = self.dfreturns.shift(-1)     

        self.chml.reset_index(inplace=True)
        self.gp.reset_index(inplace=True)
        self.tvls.reset_index(inplace=True)
        self.fees.reset_index(inplace=True)
        self.mcaps.reset_index(inplace=True)


        self.generate_positions()

    def generate_positions(self) :
        for index, row in self.chml.iterrows():
          print (index)
          if index % 7 ==0 :
            print(index)
            # Create a new dataframe to store protocol data for the current date
            data = pd.DataFrame(columns = ['Protocol','C-HML','GP', 'TVL'])


            for j,col in enumerate(self.chml.columns):
                # Create a new row with protocol data
                new_row = {'Protocol': col, 'C-HML':row[j], 'GP': self.gp.iloc[index][j], 'TVL': self.tvls.iloc[index][j]}
                #new_row = {'Protocol': col, 'C-HML':np.random.rand(100)[0], 'GP': np.random.rand(100)[0], 'TVL':np.random.rand(100)[0]}
                # Append the new row to the data dataframe
                data = data.append(new_row, ignore_index = True)
                
            print (data)

            condition  = (pd.isna(data['C-HML'])) |  (pd.isna(data['GP']))



            # Remove coins that meet the condition and store them in the removed_data dataframe
            removed_data = data[condition]
            removed_data['Weights'] = np.nan
            # Keep coins that meet the inverse condition in  the data dataframe
            data_chml = data[~condition]

            col_chml = data_chml['C-HML']
            q1 = col_chml.quantile(0.3)
            q2 = col_chml.quantile(0.7)

            data_up = data_chml.loc[col_chml > q2]
            data_middle = data_chml.loc[(q1 < col_chml) & (col_chml <= q2)]
            data_down = data_chml.loc[col_chml <= q1]

            chml_up = data_up['TVL']
            chml_middle = data_middle['TVL']
            chml_down = data_down['TVL']


            sum_up = sum(data_up ['TVL'])
            sum_middle = sum(data_middle['TVL'])
            sum_down = sum(data_down['TVL'])


            weights_up = chml_up/sum_up
            weights_middle = chml_middle/sum_middle
            weights_down = chml_down/sum_down

            # Assign the weights to each coin based on size and momentum, multiplied by the investment strategy (sign)
            data_up['Weights'] = weights_up
            data_middle['Weights'] = 0
            data_down['Weights'] = -weights_down

            # Concatenate the size portfolio with the weights of all coins
            chml_p = pd.concat([removed_data[['Protocol','Weights']],data_up[['Protocol','Weights']],data_middle[['Protocol','Weights']],data_down[['Protocol','Weights']]])


            chml_p['Protocol'] = chml_p['Protocol'].astype(str)
            chml_p = chml_p.sort_values('Protocol')

            self.chml_positions = self.chml_positions.reset_index(drop=True)
            weights = chml_p['Weights'].T

            self.chml_positions = self.chml_positions.append(weights, ignore_index=False)       


            data_gp = data[~condition]

            col_gp = data_gp['GP']
            q1 = col_chml.quantile(0.3)
            q2 = col_chml.quantile(0.7)

            data_up = data_gp.loc[col_gp > q2]
            data_middle = data_gp.loc[(q1 < col_gp) & (col_gp <= q2)]
            data_down = data_gp.loc[col_gp <= q1]

            gp_up = data_up['TVL']
            gp_middle = data_middle['TVL']
            gp_down = data_down['TVL']


            sum_up = sum(data_up ['TVL'])
            sum_middle = sum(data_middle['TVL'])
            sum_down = sum(data_down['TVL'])


            weights_up = gp_up/sum_up
            weights_middle = gp_middle/sum_middle
            weights_down = gp_down/sum_down

            # Assign the weights to each coin based on size and momentum, multiplied by the investment strategy (sign)
            data_up['Weights'] = weights_up
            data_middle['Weights'] = 0
            data_down['Weights'] = -weights_down

            # Concatenate the size portfolio with the weights of all coins
            gp_p = pd.concat([removed_data[['Protocol','Weights']],data_up[['Protocol','Weights']],data_middle[['Protocol','Weights']],data_down[['Protocol','Weights']]])


            gp_p['Protocol'] = gp_p['Protocol'].astype(str)
            gp_p = gp_p.sort_values('Protocol')

            self.gp_positions = self.gp_positions.reset_index(drop=True)
            weights = gp_p['Weights'].T

            self.gp_positions = self.gp_positions.append(weights, ignore_index=False)

    def generate_chml_portfolio_returns(self):
        """
        Function generating  the C-HML portfolio returns
        """

        rets_rep = pd.DataFrame(np.repeat(self.chml_positions.values, 7, axis=0), columns=self.chml_positions.columns)
        self.chml_returns = rets_rep.mul(self.returns_shifted).sum(axis = 1)
        return self.chml_returns
    
    def generate_gp_portfolio_returns(self):
        """
        Function generating  the gp portfolio returns
        """

        rets_rep = pd.DataFrame(np.repeat(self.gp_positions.values, 7, axis=0), columns=self.gp_positions.columns)
        self.gp_returns = rets_rep.mul(self.returns_shifted).sum(axis = 1)
        return self.gp_returns







