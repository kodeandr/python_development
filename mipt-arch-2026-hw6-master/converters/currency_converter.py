from abc import ABC, abstractmethod

class CurrencyConverter(ABC):
    @abstractmethod
    def convert_usd_to_eur(self, amount):
        pass

    @abstractmethod
    def convert_usd_to_gbp(self, amount):
        pass

    @abstractmethod
    def convert_usd_to_rub(self, amount):
        pass

    @abstractmethod
    def convert_usd_to_cny(self, amount):
        pass