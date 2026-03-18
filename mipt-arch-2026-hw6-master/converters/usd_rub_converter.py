import requests
from converters import CurrencyConverter

class UsdRubConverter(CurrencyConverter):
    def __init__(self):
        self.rates = self.get_rates()

    def get_rates(self):
        response = requests.get("https://api.exchangerate-api.com/v4/latest/USD")
        data = response.json()
        return data['rates']
    
    def convert_usd_to_eur(self, amount):
        print('This is not USD to EUR converter')

    def convert_usd_to_gbp(self, amount):
        print('This is not USD to GBP converter')

    def convert_usd_to_rub(self, amount):
        return amount * self.rates['RUB']

    def convert_usd_to_cny(self, amount):
        print('This is not USD to CNY converter')