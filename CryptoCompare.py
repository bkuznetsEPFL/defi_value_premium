import pandas as pd
import requests
from os.path import join
from tqdm import tqdm
from PathManager import PathManager


class Keys:
    ENTERPRISE_KEY = (
        '944903d112f984bfb475209cfa6e802c44dfa72f582a7f14f50961fca1a31d6e'
    )

    THOMAS_KEY = (
        '7d9161a5c19464276f169286ae5a8d9a716de6dacecf825e14167c6783dc4348'
    )


class CryptoCompare(Keys):
    """
    Official CryptoCompare API with enterprise subscription.
    See https://min-api.cryptocompare.com/documentation
    for documentation, to check if API key is valid and
    to try various endpoints.
    """

    def __init__(self):
        self.key = Keys.ENTERPRISE_KEY

    def daily_pair_ohlc(
            self, fsym: str, tsym: str, limit: str, e: str = 'CCCAGG'):
        """ fetches daily historical OHLC prices for 'limit'
        dates for fsym/tsym currency pair from 'e' exchange """
        return requests.get(
            (f"https://min-api.cryptocompare.com"
             f"/data/v2/histoday?"
             f"fsym={fsym}&tsym={tsym}&limit={limit}&e={e}&api_key={self.key}")
        )

    def available_coin_list(self):
        """ returns a list of all coins for which we currently
        get blockchain data from IntoTheBlock """
        return requests.get(
            (f"https://min-api.cryptocompare.com"
             f"/data/blockchain/list?api_key={self.key}")
        )

    def blockchain_historical_daily(self, fsym: str, limit: str):
        """ retrieves daily aggregated blockchain data for
        the requested coin, back through time"""
        return requests.get(
            (f"https://min-api.cryptocompare.com"
             f"/data/blockchain/histo/day?"
             f"fsym={fsym}&limit={limit}&api_key={self.key}")
        )

    def get_ohlcv_dataframe(
            self, fsym: str, tsym: str, limit: str, e: str = 'CCCAGG'):
        """ retrieves OHLCV pd.DataFrame for a specified coin,
        parameters are same as daily_pair_ohlc(), values are
        based on 00:00:00 GMT time """
        resp_json = self.daily_pair_ohlc(fsym, tsym, limit, e).json()
        ohlcv = resp_json.get('Data').get('Data')

        ohlcv = pd.DataFrame(ohlcv)

        try:
            time = ohlcv.time
            ohlcv['time'] = pd.to_datetime(time, unit='s')

            ohlcv['fsym'] = fsym
            ohlcv['tsym'] = tsym

            ohlcv = ohlcv[['fsym', 'tsym', 'time', 'high', 'low',
                           'open', 'close', 'volumefrom', 'volumeto']]

            return ohlcv

        except AttributeError:
            # market does not exist for fsym
            return pd.DataFrame()

    def get_blockchain_dataframe(self, fsym: str, limit: str):
        """ retrieves OHLCV pd.DataFrame for a specified coin,
        parameters are same as daily_pair_ohlc(), values are
        based on 00:00:00 GMT time """
        resp_json = self.blockchain_historical_daily(fsym, limit).json()
        block = resp_json.get('Data').get('Data')

        block = pd.DataFrame(block)
        time = block.get('time')
        block['time'] = pd.to_datetime(time, unit='s')

        return block

    def save_panel_ohlc(
            self, fsym_list: list, tsym: str, dir_: str,
            suffix: str, limit: str = 2000, e: str = 'CCCAGG'):
        """ saves panel ohlcv pd.DataFrame for a list of
        fsym for a fixed tsym to dir_ """
        ohlcvs = [self.get_ohlcv_dataframe(fsym, tsym, limit, e)
                  for fsym in tqdm(fsym_list)]
        pd.concat(ohlcvs, 0).to_csv(
            join(dir_, f'ohlcv_panel_{tsym}_{limit}_{e}_{suffix}.csv'))

    def save_panel_blockchain(
            self, fsym_list: list, dir_: str, suffix: str, limit: str = 2000):
        """ saves panel blockchain data pd.DataFrame for a
        list of fsym to dir_ """
        blocks = [self.get_blockchain_dataframe(fsym, limit)
                  for fsym in tqdm(fsym_list)]
        pd.concat(blocks, 0).to_csv(
            join(dir_, f'blockchain_panel_{limit}_{suffix}.csv'))


if __name__ == '__main__':
    """ test """
    save_ohlcv_2000_all = True
    save_blockchain_2000_all = True

    cc = CryptoCompare()

    all_coins = cc.available_coin_list().json()
    all_coins = [s for s in all_coins.get('Data')]

    if save_ohlcv_2000_all:
        """ saves a panel OHLCV pd.DataFrame 
        with tsym='USD' and limit='2000' """
        cc.save_panel_ohlc(fsym_list=all_coins,
                           tsym='USD',
                           suffix='all',
                           dir_=PathManager.ohlcv_panel_USD_2000_all)

    if save_blockchain_2000_all:
        """ saves a panel blockchain data 
        pd.DataFrame with limit='2000' """
        cc.save_panel_blockchain(fsym_list=all_coins,
                                 suffix='all',
                                 dir_=PathManager.blockchain_panel_2000_all)
