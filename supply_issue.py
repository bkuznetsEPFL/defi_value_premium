import requests
import pandas as pd
from PathManager import PathManager

if __name__ == '__main__':
    # indeed no UNI or LIDO, 809 coins total which is suspiciously small
    supply = pd.read_csv('data/blockchain_panel_2000_all.csv')
    supply = supply[['symbol', 'time', 'current_supply']]

    # indeed 809 coins which blockchain data available
    key = '944903d112f984bfb475209cfa6e802c44dfa72f582a7f14f50961fca1a31d6e'
    coins = requests.get(f'https://min-api.cryptocompare.com/data/blockchain/'
                         f'list?api_key={key}').json()['Data'].keys()

    breakpoint()
