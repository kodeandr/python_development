from converters.providers.base import RateProvider
from .base import Converter

class USDToRUBConverter(Converter):
    """Конвертер из USD в RUB."""

    def __init__(self, provider: RateProvider) -> None:
        self._provider = provider

    def convert(self, amount: float) -> float:
        rate = self._provider.get_rate("RUB")
        return amount * rate