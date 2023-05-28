import requests
import json
import pandas as pd


class Llama:
    """
    Official DefiLlama open API, see https://defillama.com/docs/api
    for documentation.
    """

    @staticmethod
    def protocol(protocol):
        """ get historical TVL of a protocol
        and breakdowns by token and chain """
        # pass protocol slug
        url = f'https://api.llama.fi/protocol/{protocol}'
        headers = {'accept': '*/*'}
        response = requests.get(url, headers=headers)

        return response

    @staticmethod
    def all_protocols():
        """ lists all protocols on defillama along
        with their current tvl """
        url = f'https://api.llama.fi/protocols'
        headers = {'accept': '*/*'}
        response = requests.get(url, headers=headers)

        return response

    @staticmethod
    def fees(protocol):
        """ gets historical summary of protocol fees
        and revenue """
        # pass protocol slug
        url = f'https://api.llama.fi/summary/fees/{protocol}'
        headers = {'accept': '*/*'}
        response = requests.get(url, headers=headers)

        return response


if __name__ == '__main__':

    Ll = Llama()

    save_tvls = False
    save_fees = True
    save_mcaps = True

    fetch = Ll.all_protocols().json()
    all_protocols = []
    for protocol in fetch:
        all_protocols.append(protocol.get('slug'))


    if save_tvls:
        """save total value locked data 
        to csv for all protocols for all dates"""
        tvls = pd.DataFrame(columns=all_protocols)
        tvls['date']=pd.date_range(start='2019-01-04', end='2023-03-31').strftime('%Y-%m-%d')
        tvls.set_index('date', inplace=True)
        for protocol in all_protocols:
                fetch = Ll.protocol(protocol)
                fetch = json.loads(fetch.content.decode('utf-8'))
                tvl_hist = fetch.get('chainTvls')
                if (tvl_hist is not None):
                    tvl_hist = list(tvl_hist.values())[0]
                    if (tvl_hist is not None):
                        tvl_hist = tvl_hist.get('tvl')
                        for pair in tvl_hist:
                            date = pair.get('date')   
                            date = pd.to_datetime(date, unit='s').date()
                            tvl = pair.get('totalLiquidityUSD')
                            tvls.at[str(date), str(protocol)] = tvl
                        print ("ok")
                            

                            
        tvls = tvls.fillna(0)
        tvls.to_csv('data/tvls.csv', sep=',', index=True)

    if save_fees:
        """ save fees data 
        to csv for all protocols for all dates"""
        fees = pd.DataFrame(columns=all_protocols)
        fees['date']=pd.date_range(start='2019-01-04', end='2023-03-31').strftime('%Y-%m-%d')
        fees.set_index('date', inplace=True)
        for protocol in all_protocols:
                fetch = Ll.fees(protocol)
                try:
                   fetch = json.loads(fetch.content.decode('utf-8'))
                except ValueError:
                    print("error")
                    continue
                fees_hist = fetch.get('totalDataChart')
                if (fees_hist is not None):
                    for pair in fees_hist:
                            date = pair[0]
                            date = pd.to_datetime(date, unit='s').date()
    
                            fee = pair[1]
                            fees.at[str(date), str(protocol)] = fee
                    print(protocol)
                            

                            
        fees = fees.fillna(0)
        fees.to_csv('data/fees.csv', sep=',', index=True)   

    if save_mcaps:
        """ save market cap data 
        to csv for all protocols for all dates"""
        mcaps = pd.DataFrame(columns=all_protocols)
        mcaps['date']=pd.date_range(start='2019-01-04', end='2023-03-31').strftime('%Y-%m-%d')
        mcaps.set_index('date', inplace=True)
        for protocol in all_protocols:
                fetch = Ll.protocol(protocol)
                fetch = json.loads(fetch.content.decode('utf-8'))
                tokens_data = fetch.get('tokens')
                if (tokens_data is not None):
                    for pair in tokens_data:
                            date = pair.get('date')
                            date = pd.to_datetime(date, unit='s').date()
                            mcap = 0
                            tokens = pair.get('tokens')
                            for key, val in tokens.items():
                                mcap+=val
                            mcaps.at[str(date), str(protocol)] = mcap
                            

                            
        mcaps = mcaps.fillna(0)
        mcaps.to_csv('data/mcaps.csv', sep=',', index=True)