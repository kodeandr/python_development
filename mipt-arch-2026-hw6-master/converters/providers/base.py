from abc import ABC, abstractmethod

class RateProvider(ABC):
    """Базовый класс для получения курсов валют."""

    @abstractmethod
    def get_rate(self, currency: str) -> float:
        """
        Возвращает курс указанной валюты по отношению к USD.

        Args:
            currency: Код валюты (например, "EUR").

        Returns:
            Курс валюты.
        """
        pass