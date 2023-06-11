import requests
import json
import pandas as pd
import CryptoCompare as cc


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
    
    def rev(protocol):
        """ gets historical summary of protocol revenue """
        # pass protocol slug
        url = f'https://api.llama.fi/summary/fees/{protocol}?dataType=dailyRevenue'
        headers = {'accept': '*/*'}
        response = requests.get(url, headers=headers)

        return response
  


if __name__ == '__main__':

    Ll = Llama()

    save_tvls = False
    save_fees = False
    save_mcaps = False


    fetch = Ll.all_protocols().json()
    all_protocols = []
    for protocol in fetch:
        all_protocols.append((protocol.get('slug'), protocol.get('symbol')))





    if save_tvls:
        """save total value locked data 
        to csv for all protocols for all dates"""
        slugs = [slug for slug, symbol in all_protocols]
        tvls = pd.DataFrame(columns=slugs)
        tvls['date']=pd.date_range(start='2018-01-11', end='2023-06-07').strftime('%Y-%m-%d')
        tvls.set_index('date', inplace=True)
        for protocol in slugs:
                fetch = Ll.protocol(protocol)
                fetch = json.loads(fetch.content.decode('utf-8'))
                tvl_hist = fetch.get('chainTvls')
                if (tvl_hist is not None ):
                        tvl_hist = list(tvl_hist.values())
                        for chain in tvl_hist:
                            if (tvl_hist is not None):

                                tvl_hist = chain.get('tvl')
                                for pair in tvl_hist:
                                    date_unix = pair.get('date') 
                                    date = pd.to_datetime(date_unix, unit='s').date()
                                    tvl = pair.get('totalLiquidityUSD')
                                    if pd.isna(tvls.at[str(date), str(protocol)]):
                                        tvls.at[str(date), str(protocol)] = tvl 
                                    else:
                                        tvls.at[str(date), str(protocol)] += tvl  

                
            
                                
                            

                            
        tvls = tvls.fillna(0)
        tvls.to_csv('data/tvls2.csv', sep=',', index=True)


    if save_fees:
        """ save fees data 
        to csv for all protocols for all dates"""
        print("hi")
        slugs = [slug for slug, symbol in all_protocols]
        fees = pd.DataFrame(columns=slugs)
        fees['date']=pd.date_range(start='2018-01-11', end='2023-06-07').strftime('%Y-%m-%d')
        fees.set_index('date', inplace=True)
        for protocol in slugs:
                fetch = Ll.fees(protocol)
                try:
                   fetch = json.loads(fetch.content.decode('utf-8'))
                except ValueError:
                    print("error")
                    continue
                fees_hist = fetch.get('totalDataChart')
                print("hi")
                if (fees_hist is not None):
                    for pair in fees_hist:
                            date = pair[0]
                            date = pd.to_datetime(date, unit='s').date()
    
                            fee = pair[1]
                            fees.at[str(date), str(protocol)] = fee
                    print(protocol)
                            

                            
        fees = fees.fillna(0)
        fees.to_csv('data/fees2.csv', sep=',', index=True)   

    if save_mcaps:
        """ save market cap data 
        to csv for all protocols for all dates"""
        cc = cc.CryptoCompare()
        slugs = [slug for slug, symbol in all_protocols]
        symbols = [symbol for slug, symbol in all_protocols]

        prices = pd.DataFrame(columns=slugs)
        prices['date']=pd.date_range(start='2018-01-11', end='2023-06-07').strftime('%Y-%m-%d')
        prices.set_index('date', inplace=True)

        supplies = pd.DataFrame(columns=slugs)
        supplies['date']=pd.date_range(start='2018-01-11', end='2023-06-07').strftime('%Y-%m-%d')
        supplies.set_index('date', inplace=True)

        mcaps = pd.DataFrame(columns=slugs)
        mcaps['date']=pd.date_range(start='2018-01-11', end='2023-06-07').strftime('%Y-%m-%d')
        mcaps.set_index('date', inplace=True)

        for slug,symbol in all_protocols:
            print(symbol)
            fetch = cc.daily_pair_ohlc(symbol, 'USD', limit=1679, toTs='1685998800')
            fetch = json.loads(fetch.content.decode('utf-8'))
            price_data = fetch.get('Data').get('Data')

            fetch2 = cc.blockchain_historical_daily(symbol, limit=1679, toTs='1685998800')
            fetch2 = json.loads(fetch2.content.decode('utf-8'))
            supply_data = fetch2.get('Data').get('Data')

                
            if price_data is not None and supply_data is not None:

                for x in price_data:
                    print(x)
                    date = x.get('time')
                    date = pd.to_datetime(date, unit='s').date()
                    price = x.get('close')
                    prices.at[str(date), str(slug)] = price

                for x in supply_data:
                    print(x)
                    date = x.get('time')
                    date = pd.to_datetime(date, unit='s').date()
                    supply = x.get('current_supply')
                    supplies.at[str(date), str(slug)] = supply
                
        mcaps = prices.mul(supply)
        mcaps = mcaps.fillna(0)
        prices.to_csv('data/prices2.csv', sep=',', index=True)
        supplies.to_csv('data/supplies2.csv', sep=',', index=True)
        mcaps.to_csv('data/mcaps2.csv', sep=',', index=True)
