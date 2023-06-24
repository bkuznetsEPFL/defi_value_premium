import requests
from tqdm import tqdm


if __name__ == '__main__':
    headers = {'accept': '*/*'}

    # list all protocols
    res = requests.get('https://api.llama.fi/protocols', headers=headers)
    slugs = []
    for item in res.json():
        slugs.append(item['slug'])

    count = 0
    for slug in tqdm(slugs):
        res = requests.get(f'https://api.llama.fi/summary/fees/{slug}',
                             headers=headers)
        if res.status_code == 200:
            count += 1

    # indeed 175 protocols for which revenue data are available
    breakpoint()

