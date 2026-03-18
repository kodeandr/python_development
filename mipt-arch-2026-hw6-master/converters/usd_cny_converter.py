import requests, json, time, os
from converters import CurrencyConverter

class UsdCnyConverter(CurrencyConverter):
    def __init__(self, api_url="https://api.exchangerate-api.com/v4/latest/USD", cache_file="exchange_rates.json", cache_expiry=3600):
        self.api_url = api_url
        self.cache_file = cache_file
        self.cache_expiry = cache_expiry
        self.rates = self.get_rates()

    def _load_from_cache(self):
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    data = json.load(f)
                    if time.time() - data['timestamp'] < self.cache_expiry:
                        return data['rates']
            except (json.JSONDecodeError, KeyError):
                print("Invalid cache file. Fetching from API.")
                return None
        return None

    def _save_to_cache(self, rates):
        try:
            data = {'timestamp': time.time(), 'rates': rates}
            with open(self.cache_file, 'w') as f:
                json.dump(data, f)
        except IOError as e:
            print(f"Error saving to cache: {e}")

    def get_rates(self):
        rates = self._load_from_cache()
        if rates:
            return rates

        try:
            response = requests.get(self.api_url, timeout=5)
            response.raise_for_status()
            data = response.json()
            rates = data['rates']
            self._save_to_cache(rates)
            return rates

        except requests.exceptions.RequestException as e:
            print(f"Error fetching rates from API: {e}")
            return None
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error processing JSON response: {e}")
            return None
    
    def convert_usd_to_eur(self, amount):
        print('This is not USD to EUR converter')

    def convert_usd_to_gbp(self, amount):
        print('This is not USD to GBP converter')

    def convert_usd_to_rub(self, amount):
        print('This is not USD to RUB converter')

    def convert_usd_to_cny(self, amount):
        return amount * self.rates['CNY']