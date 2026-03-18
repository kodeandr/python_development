import requests, json, logging, time
from converters import CurrencyConverter

class UsdEurConverter(CurrencyConverter):
    def __init__(self, max_retries=3, retry_delay=2):
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.logger = self._setup_logger()
        self.rates = self.get_rates()

    def _setup_logger(self):
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        ch = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        return logger

    def get_rates(self):
        for attempt in range(self.max_retries):
            try:
                response = requests.get("https://api.exchangerate-api.com/v4/latest/USD", timeout=10)  # Добавляем тайм-аут
                response.raise_for_status()
                data = response.json()
                rates = data['rates']
                return rates

            except requests.exceptions.RequestException as e:
                self.logger.error(f"Request failed (attempt {attempt + 1}/{self.max_retries}): {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                else:
                    self.logger.error("Max retries reached.  Unable to fetch rates.")
                    return None

            except (json.JSONDecodeError, KeyError) as e:
                self.logger.error(f"Error processing JSON response: {e}")
                return None

    def convert_usd_to_eur(self, amount):
        return amount * self.rates['EUR']

    def convert_usd_to_gbp(self, amount):
        print('This is not USD to GBP converter')

    def convert_usd_to_rub(self, amount):
        print('This is not USD to RUB converter')

    def convert_usd_to_cny(self, amount):
        print('This is not USD to CNY converter')