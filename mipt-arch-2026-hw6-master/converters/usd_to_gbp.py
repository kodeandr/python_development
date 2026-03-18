from converters.providers.base import RateProvider
from .base import Converter

class USDToGBPConverter(Converter):
    """Конвертер из USD в GBP."""

    def __init__(self, provider: RateProvider) -> None:
        self._provider = provider

    def convert(self, amount: float) -> float:
        rate = self._provider.get_rate("GBP")
        return amount * rate
from .base import Converter

class USDToGBPConverter(Converter):
    """Конвертер из USD в GBP."""

    def __init__(self, provider: RateProvider) -> None:
        self._provider = provider

    def convert(self, amount: float) -> float:
        rate = self._provider.get_rate("GBP")
        return amount * rate