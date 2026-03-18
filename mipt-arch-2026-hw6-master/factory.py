from converters import (
    USDToEURConverter,
    USDToGBPConverter,
    USDToRUBConverter,
    USDToCNYConverter,
)
from converters.base import Converter
from converters.providers.api import ApiRateProvider
from converters.providers.retry import RetryRateProvider
from converters.providers.cache import CachedRateProvider
from converters.providers.base import RateProvider

class ConverterFactory:
    """Фабрика для создания конвертеров с заданными настройками."""

    _converters = {
        "EUR": USDToEURConverter,
        "GBP": USDToGBPConverter,
        "RUB": USDToRUBConverter,
        "CNY": USDToCNYConverter,
    }

    @classmethod
    def create_converter(
        cls,
        currency: str,
        use_cache: bool = True,
        use_retry: bool = True,
        api_url: str = "https://api.exchangerate-api.com/v4/latest/USD",
        timeout: int = 10,
        max_retries: int = 3,
        retry_delay: float = 2.0,
        cache_file: str = "exchange_rates.json",
        cache_expiry: int = 3600,
    ) -> Converter:
        """
        Создаёт конвертер для указанной валюты.

        Args:
            currency: Код целевой валюты (EUR, GBP, RUB, CNY).
            use_cache: Использовать кэширование.
            use_retry: Использовать повторные попытки.
            api_url: URL API для получения курсов.
            timeout: Таймаут HTTP-запроса.
            max_retries: Максимальное количество попыток.
            retry_delay: Задержка между попытками.
            cache_file: Файл для кэша.
            cache_expiry: Время жизни кэша в секундах.

        Returns:
            Конвертер, реализующий интерфейс Converter.
        """
        currency = currency.upper()
        if currency not in cls._converters:
            raise ValueError(f"Неподдерживаемая валюта: {currency}. Доступны: {list(cls._converters.keys())}")

        provider: RateProvider = ApiRateProvider(api_url=api_url, timeout=timeout)

        if use_retry:
            provider = RetryRateProvider(provider, max_retries=max_retries, delay=retry_delay)
        if use_cache:
            provider = CachedRateProvider(provider, cache_file=cache_file, cache_expiry=cache_expiry)

        converter_class = cls._converters[currency]
        return converter_class(provider)