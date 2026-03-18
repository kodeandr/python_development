import time
import json
import os
import logging
from .base import RateProvider

logger = logging.getLogger(__name__)

class CachedRateProvider(RateProvider):
    """Декоратор, добавляющий кэширование курсов в файл."""

    def __init__(self, provider: RateProvider, cache_file: str = "exchange_rates.json", cache_expiry: int = 3600) -> None:
        self._provider = provider
        self.cache_file = cache_file
        self.cache_expiry = cache_expiry

    def _load_from_cache(self) -> dict[str, float] | None:
        if not os.path.exists(self.cache_file):
            return None
        try:
            with open(self.cache_file, "r") as f:
                data = json.load(f)
            if time.time() - data["timestamp"] < self.cache_expiry:
                return data["rates"]
        except (json.JSONDecodeError, KeyError, OSError) as e:
            logger.warning(f"Ошибка чтения кэша: {e}")
        return None

    def _save_to_cache(self, rates: dict[str, float]) -> None:
        try:
            data = {"timestamp": time.time(), "rates": rates}
            with open(self.cache_file, "w") as f:
                json.dump(data, f)
        except OSError as e:
            logger.warning(f"Ошибка записи кэша: {e}")

    def get_rate(self, currency: str) -> float:
        cached_rates = self._load_from_cache()
        if cached_rates is not None and currency in cached_rates:
            return cached_rates[currency]

        rate = self._provider.get_rate(currency)

        # Если нижележащий провайдер загрузил все курсы, сохраняем весь словарь
        if hasattr(self._provider, "_rates") and self._provider._rates is not None:
            self._save_to_cache(self._provider._rates)
        else:
            self._save_to_cache({currency: rate})

        return rate