import requests
from .base import RateProvider

class ApiRateProvider(RateProvider):
    """Провайдер курсов, получающий данные через API."""

    def __init__(self, api_url: str = "https://api.exchangerate-api.com/v4/latest/USD", timeout: int = 10) -> None:
        self.api_url = api_url
        self.timeout = timeout
        self._rates: dict[str, float] | None = None

    def get_rate(self, currency: str) -> float:
        if self._rates is None:
            response = requests.get(self.api_url, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            self._rates = data["rates"]

        if currency not in self._rates:
            raise ValueError(f"Курс для валюты {currency} не найден")

        return self._rates[currency]