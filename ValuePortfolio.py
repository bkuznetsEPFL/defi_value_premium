import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


class ValuePortfolio:

    def __init__ (self):

        tvls = pd.read_csv('data/tvls.csv')
        fees = pd.read_csv('data/fees.csv')
        mcaps = pd.read_csv('data/mcaps.csv')


        # self.tvls = pd.to_numeric(tvls.head(1600).sort_values(by='date', ascending=True), errors='coerce')
        # self.fees = pd.to_numeric(fees.head(1600).sort_values(by='date', ascending=True), errors='coerce')
        # self.mcaps = pd.to_numeric(mcaps.head(1600).sort_values(by='date', ascending=True), errors='coerce')

        self.tvls = tvls.head(1600).sort_values(by='date', ascending=True).set_index('date')
        self.fees = fees.head(1600).sort_values(by='date', ascending=True).set_index('date')
        self.mcaps = mcaps.head(1600).sort_values(by='date', ascending=True).set_index('date')

        self.tvls = self.tvls.replace(0, np.nan)
        self.fees = self.fees.replace(0, np.nan)
        self.mcaps = self.mcaps.replace(0, np.nan)  

        self.chml = self.tvls / self.mcaps
        self.gp = self.fees / self.tvls  

        self.dfreturns = (self.tvls - self.tvls.shift(1))/self.tvls.shift(1)

        self.returns_shifted = self.dfreturns.shift(-1)     

        print(self.dfreturns)



        self.chml_positions = pd.DataFrame()
        self.gp_positions = pd.DataFrame()        


        self.chml = self.chml.tail(50)
        self.gp = self.gp.tail(50)
        self.tvls= self.tvls.tail(50)
        self.fees = self.fees.tail(50)
        self.mcaps = self.mcaps.tail(50)
        self.dfreturns = self.dfreturns.tail(50)
        self.returns_shifted = self.returns_shifted.tail(50)
        


        self.chml.reset_index(inplace=True)
        self.gp.reset_index(inplace=True)
        self.tvls.reset_index(inplace=True)
        self.fees.reset_index(inplace=True)
        self.mcaps.reset_index(inplace=True)



        self.generate_positions()
        self.chml_positions.to_csv('chml_positions.csv')
        self.gp_positions.to_csv('gp_positions.csv')
        self.dfreturns.to_csv('dfreturns.csv')

    def generate_positions(self) :
        for index, row in self.chml.iterrows():
          print (index)
          if index % 7 ==0 :
            print(index)
            # Create a new dataframe to store protocol data for the current date
            data = pd.DataFrame(columns = ['Protocol','C-HML','GP', 'TVL'])


            for j,col in enumerate(self.chml.columns):
                # Create a new row with protocol data
                # row[j]
                # self.gp.iloc[index][j]
                new_row = {'Protocol': col, 'C-HML':row[j], 'GP': self.gp.iloc[index][j], 'TVL': self.tvls.iloc[index][j]}

                #new_row = {'Protocol': col, 'C-HML':np.random.rand(100)[0], 'GP': np.random.rand(100)[0], 'TVL':np.random.rand(100)[0]}
                # Append the new row to the data dataframe
                data = data.append(new_row, ignore_index = True)
            print("data")
            print (data)

            condition  = (pd.isna(data['C-HML'])) |  (pd.isna(data['GP'])) | (pd.isna(data['TVL']))



            # Remove coins that meet the condition and store them in the removed_data dataframe
            removed_data = data[condition]
            removed_data['Weights'] = np.nan
            # Keep coins that meet the inverse condition in  the data dataframe

            data_chml = data[~condition]
            col_chml = data_chml['C-HML']
            col_chml = pd.to_numeric(data_chml['C-HML'], errors='coerce')

            
            # print(len(col_chml))

            # if (len(col_chml) <= 1):
            #     empty_chml = pd.DataFrame( columns=self.chml_positions.columns) 
            #     empty_gp = pd.DataFrame( columns=self.gp_positions.columns)
            #     self.chml_positions = self.chml_positions.append(empty_chml, ignore_index=False)
            #     self.gp_positions = self.gp_positions.append(empty_gp, ignore_index=False)

            
            #     continue
            # else : 
        
                # print(len(col_chml))
                #print("/(//////////////////////////////////////")
            print("col_chml")
            print(col_chml)
                #print("///////////////////////////////////////")
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
            print("data_up")
            print(data_up)

            # Concatenate the size portfolio with the weights of all coins
            chml_p = pd.concat([removed_data[['Protocol','Weights']],data_up[['Protocol','Weights']],data_middle[['Protocol','Weights']],data_down[['Protocol','Weights']]])


            chml_p['Protocol'] = chml_p['Protocol'].astype(str)
            chml_p = chml_p.sort_values('Protocol')

            self.chml_positions = self.chml_positions.reset_index(drop=True)
            weights = chml_p['Weights'].T
            print("weights")

            self.chml_positions = self.chml_positions.append(weights, ignore_index=False)       
            print(self.chml_positions)

            data_gp = data[~condition]

            col_gp = data_gp['GP']
            col_gp = pd.to_numeric(data_gp['GP'], errors='coerce')

            q1 = col_chml.quantile(0.3)
            q2 = col_chml.quantile(0.7)

            data_up = data_gp.loc[col_gp > q2]
            data_middle = data_gp.loc[(q1 < col_gp) & (col_gp <= q2)]
            data_down = data_gp.loc[col_gp <= q1]

            gp_up = data_up['TVL']
            gp_middle = data_middle['TVL']
            gp_down = data_down['TVL']
            print("gp_up")
            print(gp_up)

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
            self.chml_positions.to_csv('chml_positions.csv')
            self.gp_positions.to_csv('gp_positions.csv')

    def generate_chml_portfolio_returns(self):
        """
        Function generating  the C-HML portfolio returns
        """

        # rets_rep = pd.DataFrame(np.repeat(self.chml_positions.values, 7, axis=0), columns=self.chml_positions.columns)
        # self.chml_returns = rets_rep.mul(self.returns_shifted).sum(axis = 1)
        # self.chml_returns.to_csv('chml_returns.csv')
        # return self.chml_returns  
        pos_rep = pd.DataFrame(np.repeat(self.chml_positions.values, 7, axis=0), columns=self.chml_positions.columns)  
        pos_rep = pos_rep.drop(pos_rep.columns[0], axis=1)  
        pos_rep.columns = pos_rep.columns.astype(int)   
        rets_shifted = self.returns_shifted.copy()
        rets_shifted.columns = range(len(rets_shifted.columns))
        rets_shifted = rets_shifted.drop(rets_shifted.columns[0], axis=1)
        rets_shifted = rets_shifted.reset_index(drop=True)
        print("CHMLLLLLLLLLLLLLLLLLLLLLLLL")   
        print(pos_rep)
        print(rets_shifted)
        print("MULL     CHMLLLLLLLLLLLLLLLLLLLLLLLL")
        self.chml_returns = pos_rep.mul(rets_shifted)  
        print(self.chml_returns)
        print("SUMMMMM")
        self.chml_returns = self.chml_returns.sum(axis = 1)
        print(self.chml_returns)
        self.chml_returns.to_csv('chml_returns.csv')  
        return self.chml_returns
    
    def generate_gp_portfolio_returns(self):
        """
        Function generating  the gp portfolio returns
        """

        pos_rep = pd.DataFrame(np.repeat(self.gp_positions.values, 7, axis=0), columns=self.gp_positions.columns)  
        pos_rep = pos_rep.drop(pos_rep.columns[0], axis=1)  
        pos_rep.columns = pos_rep.columns.astype(int)   
        rets_shifted = self.returns_shifted.copy()
        rets_shifted.columns = range(len(rets_shifted.columns))
        rets_shifted = rets_shifted.drop(rets_shifted.columns[0], axis=1)
        rets_shifted = rets_shifted.reset_index(drop=True)
        self.gp_returns = pos_rep.mul(rets_shifted).sum(axis = 1)
        self.gp_returns.to_csv('gp_returns.csv')
        return self.gp_returns


    def plotter(self,chml, gp):
        """
        Function plotting the cumulative portfolio returns, using their returns (csv)
        """




        headers = ['CHML Portfolio Returns']
        df_market = chml.to_frame()
        df_market.columns = headers

        df_market['date'] = pd.date_range(end= '22/04/2023', periods=len(df_market), freq='D')
        df_market.set_index(['date'],inplace=True)

        df_market['CHML Portfolio Returns'] +=1
        df_market = df_market.cumprod()

        headers = ['GP Portfolio Returns']

        df_size = gp.to_frame()
        df_size.columns =  headers
        df_size = df_size.replace([np.inf, -np.inf], np.nan).dropna(axis=0)
        df_size = df_size.mask(df_size.eq('None')).dropna()
        df_size['date'] = pd.date_range(end= '22/04/2023', periods=len(df_size), freq='D')
        df_size.set_index(['date'],inplace=True)

        df_size['GP Portfolio Returns'] +=1
        df_size = df_size.cumprod()

        # Create a figure and axis object
        fig, ax = plt.subplots(figsize=(10, 5))

        # Plot the Market Portfolio Returns
        df_market.plot(ax=ax)

        # Plot the Size Portfolio Returns
        df_size.plot(ax=ax)

        # Plot the Momentum Portfolio Returns

        # Set the title and axis labels
        ax.set_title('Portfolio Returns')
        ax.set_xlabel('Date')
        ax.set_ylabel('Cumulative Returns')

        # Show the plot
        plt.show()







