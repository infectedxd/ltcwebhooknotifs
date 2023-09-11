import requests
from dhooks import Webhook, Embed
import time

DISCORD_WEBHOOK_URL = 'https://canary.discord.com/api/webhooks/xx/xxx'
LTC_ADDRESS = 'ltc1q4287zq8zxpusyvc70sjh585p69p55uwdq68hct'

ltcpriceusd = 0

def fetch_ltc_price():
    global ltcpriceusd
    try:
        response = requests.get('https://min-api.cryptocompare.com/data/price?fsym=LTC&tsyms=USD')
        data = response.json()
        ltcpriceusd = data['USD']
    except Exception as error:
        print('Error fetching LTC price:', error)

def send(embed_data):
    webhook = Webhook(DISCORD_WEBHOOK_URL)
    webhook.send(embed=embed_data)

def ltc_notifier():
    endpoint = f'https://api.blockcypher.com/v1/ltc/main/addrs/{LTC_ADDRESS}/full'
    initial_tx_count = 0

    try:
        response = requests.get(endpoint)
        data = response.json()
        initial_tx_count = data['n_tx']
        print('Connected with address:', LTC_ADDRESS)
        print(f'Initial transaction count: {initial_tx_count}')
        print('- I N F E C E T E D')
    except Exception as error:
        print('Error:', error)
        return

    while True:
        time.sleep(15)

        try:
            response = requests.get(endpoint)
            data = response.json()

            if response.status_code == 429:
                print(data)
                break

            current_tx_count = data['n_tx']
            print(current_tx_count)

            if current_tx_count > initial_tx_count:
                tx_data = data['txs'][0]
                tx_hash = tx_data['hash']
                outputs = tx_data['outputs']
                ltc_amount = 0
                usd_amount = 0

                for output in outputs:
                    if output['addresses'][0] == LTC_ADDRESS:
                        ltc_amount = output['value'] / 1e8
                        usd_amount = ltc_amount * ltcpriceusd

                usd_amount_str = f'{usd_amount:.2f}'
                ltc_amount_str = f'{ltc_amount:.8f}'

                embed_data = Embed(
                    title='LTC Notifier',
                    description=f'**Hash:** [{tx_hash}](https://blockchair.com/litecoin/transaction/{tx_hash})\n'
                                f'**Amount:** `{ltc_amount_str} LTC`\n'
                                f'**Now:** `${usd_amount_str} USD`',
                    color=0xFFFFFF
                )

                embed_data.set_footer(text='infected.xd')
                send(embed_data)
                initial_tx_count = current_tx_count

        except Exception as error:
            print('Error: ', error)

if __name__ == "__main__":
    fetch_ltc_price()
    ltc_notifier()
