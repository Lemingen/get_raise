from abc import ABC, abstractmethod
from decimal import Decimal


class BaseApi(ABC):
    """Абстрактный базовый класс для работы с API курсов валют.

    Определяет интерфейс для получения курсов валют и выполнения конверсий валют.
    Дочерние классы должны реализовать указанные методы.

    Атрибуты:
        Нет
    """

    @abstractmethod
    async def get_currency_rate(self, currency_code: str) -> Decimal:
        """Получить курс валюты относительно базовой валюты.

        Аргументы:
            currency_code (str): Код валюты (например, 'USD', 'EUR').

        Возвращает:
            Decimal: Курс указанной валюты относительно базовой валюты.

        Исключения:
            NotImplementedError: Если метод не реализован в дочернем классе.
        """
        pass

    @abstractmethod
    async def exchange(
        self, from_currency: str, to_currency: str, amount: Decimal
    ) -> Decimal:
        """Конвертировать сумму из одной валюты в другую относительно базовой валюты.

        Аргументы:
            from_currency (str): Код валюты, из которой конвертируем (например, 'USD').
            to_currency (str): Код валюты, в которую конвертируем (например, 'EUR').
            amount (Decimal): Сумма для конвертации.

        Возвращает:
            Decimal: Сконвертированная сумма в целевой валюте.

        Исключения:
            NotImplementedError: Если метод не реализован в дочернем классе.
        """
        pass
