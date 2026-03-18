from converters.providers.base import RateProvider
from .base import Converter

class USDToEURConverter(Converter):
    """Конвертер из USD в EUR."""

    def __init__(self, provider: RateProvider) -> None:
        self._provider = provider

    def convert(self, amount: float) -> float:
        rate = self._provider.get_rate("EUR")
        return amount * rate