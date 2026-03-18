from abc import ABC, abstractmethod

class Converter(ABC):
    """Базовый класс для всех конвертеров валют."""

    @abstractmethod
    def convert(self, amount: float) -> float:
        """
        Конвертирует указанную сумму из USD в целевую валюту.

        Args:
            amount: Сумма в долларах США.

        Returns:
            Сумма в целевой валюте.
        """
        pass