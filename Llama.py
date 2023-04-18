import requests


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
    """ test """
    Ll = Llama()

    protocols = Ll.all_protocols().json()
    tvl = Ll.protocol('uniswap').json()
    revenue = Ll.fees('uniswap').json()
