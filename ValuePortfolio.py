import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


class ValuePortfolio:

    def __init__ (self):

        tvls = pd.read_csv('tvls2.csv')
        fees = pd.read_csv('fees2.csv')
        mcaps = pd.read_csv('mcaps2.csv')
        prices = pd.read_csv('prices2.csv')


        # self.tvls = pd.to_numeric(tvls.head(1600).sort_values(by='date', ascending=True), errors='coerce')
        # self.fees = pd.to_numeric(fees.head(1600).sort_values(by='date', ascending=True), errors='coerce')
        # self.mcaps = pd.to_numeric(mcaps.head(1600).sort_values(by='date', ascending=True), errors='coerce')

        self.tvls = tvls.head(1974).sort_values(by='date', ascending=True).set_index('date')
        self.fees = fees.head(1974).sort_values(by='date', ascending=True).set_index('date')
        self.mcaps = mcaps.head(1974).sort_values(by='date', ascending=True).set_index('date')
        self.prices = prices.head(1974).sort_values(by='date', ascending=True).set_index('date')

        
        # common_columns = set(self.tvls.columns).intersection(set(self.mcaps.columns), set(self.fees.columns))

        common_columns = self.tvls.columns.intersection(self.mcaps.columns)
        common_columns = sorted(common_columns)

        #        Keep only the common columns in each DataFrame
        self.tvls = self.tvls[common_columns]
        self.mcaps = self.mcaps[common_columns]
        self.fees = self.fees[common_columns]
        

    

        self.tvls = self.tvls.replace(0, np.nan)
        self.fees = self.fees.replace(0, np.nan)
        self.mcaps = self.mcaps.replace(0, np.nan)  
        self.prices = self.prices.replace(0, np.nan)

        self.chml = self.tvls / self.mcaps
        self.gp = self.fees / self.tvls  


        self.dfreturns = (self.prices - self.prices.shift(1))/self.prices.shift(1)

        self.returns_shifted = self.dfreturns.shift(-1)  

        self.dfreturns = self.dfreturns[common_columns]   
        self.returns_shifted = self.returns_shifted[common_columns]


        self.chml_positions = pd.DataFrame()
        self.gp_positions = pd.DataFrame()        


        self.chml = self.chml.tail(800)
        self.gp = self.gp.tail(800)
        self.tvls= self.tvls.tail(800)
        self.fees = self.fees.tail(800)
        self.mcaps = self.mcaps.tail(800)
        self.dfreturns = self.dfreturns.tail(800)
        self.returns_shifted = self.returns_shifted.tail(800)



        self.chml.reset_index(inplace=True, drop=True)
        self.gp.reset_index(inplace=True, drop=True)
        self.tvls.reset_index(inplace=True, drop=True)
        self.fees.reset_index(inplace=True, drop=True)
        self.mcaps.reset_index(inplace=True, drop=True)




        self.chml.to_csv('chml1-vw1.csv')
        self.gp.to_csv('gp1-vw1.csv')
        self.dfreturns.to_csv('returns-vw1.csv')  



        self.generate_positions()
        self.chml_positions.to_csv('chml_positions-vw1.csv')
        self.gp_positions.to_csv('gp_positions-vw1.csv')
        self.dfreturns.to_csv('dfreturns-vw1.csv')

    def generate_positions(self) :
        for index, row in self.chml.iterrows():
          
          if index % 7 ==0 :
          
            # Create a new dataframe to store protocol data for the current date
            data = pd.DataFrame(columns = ['Protocol','C-HML','GP', 'TVL','MCAP'])
            

            for j,col in enumerate(self.chml.columns):

                # Create a new row with protocol data
                # row[j]
                # self.gp.iloc[index][j]
                new_row = {'Protocol': col, 'C-HML':row[j], 'GP': self.gp.iloc[index][j], 'TVL': self.tvls.iloc[index][j],'MCAP': self.mcaps.iloc[index][j]}

                #new_row = {'Protocol': col, 'C-HML':np.random.rand(100)[0], 'GP': np.random.rand(100)[0], 'TVL':np.random.rand(100)[0]}
                # Append the new row to the data dataframe
                data = data.append(new_row, ignore_index = True)
          
            condition  = (pd.isna(data['C-HML']) | pd.isna(data['MCAP']) )  


            dataoriginal = data.copy()
            # Remove coins that meet the condition and store them in the removed_data dataframe
            removed_data = data[condition]
            removed_data['Weights'] = np.nan
            # Keep coins that meet the inverse condition in  the data dataframe

            data_chml = data[~condition]
            col_chml = data_chml['C-HML']
            col_chml = pd.to_numeric(data_chml['C-HML'], errors='coerce')

            
           
            q1 = col_chml.quantile(0.3)
            q2 = col_chml.quantile(0.7)



            data_up = data_chml.loc[col_chml > q2]
            data_middle = data_chml.loc[(q1 < col_chml) & (col_chml <= q2)]
            data_down = data_chml.loc[col_chml <= q1]


            # len_up = len(data_up['C-HML'])
            # len_middle = len(data_middle['C-HML'])
            # len_down = len(data_down['C-HML'])

            sum_up = sum(data_up['MCAP'])
            sum_middle = sum(data_middle['MCAP'])
            sum_down = sum(data_down['MCAP'])

            # weights_up = 1/len_up if  ((len_up != 0) & (len_down != 0)) else 0
            # weights_middle = 0 
            # weights_down = 1/len_down if  ((len_up != 0) & (len_down != 0)) else 0

            weights_up = data_up['MCAP']/sum_up
            weights_middle = 0 
            weights_down = data_down['MCAP']/sum_down 

            data_up['Weights'] = weights_up
            data_middle['Weights'] = 0
            data_down['Weights'] = -weights_down




            chml_p = pd.concat([removed_data[['Protocol','Weights']],data_up[['Protocol','Weights']],data_middle[['Protocol','Weights']],data_down[['Protocol','Weights']]])


            chml_p['Protocol'] = chml_p['Protocol'].astype(str)
            chml_p = chml_p.sort_values('Protocol')
            chml_p = chml_p.reset_index(drop=True)
            self.chml_positions = self.chml_positions.reset_index(drop=True)
            weights = chml_p['Weights'].T

            self.chml_positions = self.chml_positions.append(weights, ignore_index=False)       
            

        
            condition  = (pd.isna(data['GP']) | pd.isna(data['MCAP'])  )  

            data_gp = dataoriginal[~condition]

            removed_data = dataoriginal[condition]
            removed_data['Weights'] = np.nan    

       
            col_gp = data_gp['GP']
            col_gp = pd.to_numeric(data_gp['GP'], errors='coerce')

            q1 = col_gp.quantile(0.3)
            q2 = col_gp.quantile(0.7)

            data_up = data_gp.loc[col_gp > q2]
            data_middle = data_gp.loc[(q1 < col_gp) & (col_gp <= q2)]
            data_down = data_gp.loc[col_gp <= q1]

           
            # len_up = len(data_up['GP'])
            # len_middle = len(data_middle['GP'])
            # len_down = len(data_down['GP'])

            sum_up = sum(data_up['MCAP'])
            sum_middle = sum(data_middle['MCAP'])
            sum_down = sum(data_down['MCAP'])

            weights_up = data_up['MCAP']/sum_up 
            weights_middle = 0
            weights_down = data_down['MCAP']/sum_down  

            data_up['Weights'] = weights_up
            data_middle['Weights'] = 0
            data_down['Weights'] = -weights_down




            sumlen  = len(removed_data) + len(data_up) + len(data_middle) + len(data_down)
          

            gp_p = pd.concat([removed_data[['Protocol','Weights']],data_up[['Protocol','Weights']],data_middle[['Protocol','Weights']],data_down[['Protocol','Weights']]])
          
            gp_p['Protocol'] = gp_p['Protocol'].astype(str)
            gp_p = gp_p.sort_values('Protocol')
        
            gp_p = gp_p.reset_index(drop=True)
            
            self.gp_positions = self.gp_positions.reset_index(drop=True)
            weights = gp_p['Weights'].T
          
          

            self.gp_positions = self.gp_positions.append(weights, ignore_index=False)
            self.chml_positions.to_csv('chml_positions-vw1.csv')
            self.gp_positions.to_csv('gp_positions-vw1.csv')

    def generate_chml_portfolio_returns(self):
        """
        Function generating  the C-HML portfolio returns
        """

       
        pos_rep = pd.DataFrame(np.repeat(self.chml_positions.values, 7, axis=0), columns=self.chml_positions.columns)  
        # pos_rep = pos_rep.drop(pos_rep.columns[0], axis=1)  
        pos_rep.columns = pos_rep.columns.astype(int)   
        # self.returns_shifted = self.returns_shifted.sort_index(axis=1)
        rets_shifted = self.returns_shifted.copy()  
        rets_shifted = rets_shifted.sort_index(axis=1)
        rets_shifted.columns = range(len(rets_shifted.columns))
        rets_shifted = rets_shifted.drop(rets_shifted.columns[0], axis=1)
        rets_shifted = rets_shifted.reset_index(drop=True)
        rets_sorted = rets_shifted.sort_index(axis=1)
        pos_rep = pos_rep.sort_index(axis=1)
        pos_rep.columns = range(len(pos_rep.columns))

     

    
        self.chml_returns = pos_rep.mul(rets_sorted)  
       
        self.chml_returns = self.chml_returns.sum(axis = 1)
        self.chml_returns.to_csv('chml_returns-vw1.csv')  
        return self.chml_returns
    
    def generate_gp_portfolio_returns(self):
        """
        Function generating  the gp portfolio returns
        """
        pos_rep = pd.DataFrame(np.repeat(self.gp_positions.values, 7, axis=0), columns=self.gp_positions.columns)  
        pos_rep.columns = pos_rep.columns.astype(int) 
       
        rets_shifted = self.returns_shifted.copy()
        rets_shifted = rets_shifted.sort_index(axis=1)
        rets_shifted.columns = range(len(rets_shifted.columns)) 
      
        rets_shifted = rets_shifted.reset_index(drop=True)
        rets_sorted = rets_shifted.sort_index(axis=1)
        pos_rep = pos_rep.sort_index(axis=1)
        pos_rep.columns = range(len(pos_rep.columns))
     
        self.gp_returns = pos_rep.mul(rets_sorted)  
        
        self.gp_returns = self.gp_returns.sum(axis = 1)
        self.gp_returns.to_csv('gp_returns-vw.csv')  
        return self.gp_returns
    


    def plotter(self,chml, gp):
        """
        Function plotting the cumulative portfolio returns, using their returns (csv)
        """




        headers = ['CHML Portfolio Returns']
        df_market = chml.to_frame()
        df_market.columns = headers

        df_market['date'] = pd.date_range(end= '07/06/2023', periods=len(df_market), freq='D')
        df_market.set_index(['date'],inplace=True)

        df_market['CHML Portfolio Returns'] +=1
        df_market = df_market.cumprod()

        headers = ['GP Portfolio Returns']

        df_size = gp.to_frame()
        df_size.columns =  headers
        df_size = df_size.replace([np.inf, -np.inf], np.nan).dropna(axis=0)
        df_size = df_size.mask(df_size.eq('None')).dropna()
        df_size['date'] = pd.date_range(end= '07/06/2023', periods=len(df_size), freq='D')
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