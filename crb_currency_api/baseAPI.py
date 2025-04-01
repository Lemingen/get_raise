from abc import ABC, abstractmethod
from decimal import Decimal

class BaseAPI(ABC):
    """Абстрактный базовый класс для работы с API курсов валют."""

    @abstractmethod
    async def get_currency_rate(self, currency_code: str) -> Decimal:
        """Получает курс указанной валюты относительно базовой валюты."""
        pass

    @abstractmethod
    async def exchange(self, from_currency: str, to_currency: str, amount: Decimal) -> Decimal:
        """Конвертирует сумму из одной валюты в другую."""
        pass