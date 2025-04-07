from decimal import Decimal, getcontext
from typing import Dict
from Crb_currency_api.baseApi import BaseApi
from Crb_currency_api.api_client import ApiClient
from Crb_currency_api.cache_manager import CacheManager
from Crb_currency_api.parsers import XmlParser


class CrbRequestCurrencyApi(BaseApi):
    """Клиент API для получения курсов валют от Центрального банка России.

    Поддерживает произвольные базовые валюты и кэширование с учётом выходных.

    Атрибуты:
        url (str): URL конечной точки API ЦБ.
        DEFAULT_BASE_CURRENCY (str): Базовая валюта по умолчанию (RUB).
        base_currency (str): Настроенная базовая валюта.
        client (ApiClient): HTTP-клиент для запросов.
        cache (CacheManager): Кэш для хранения курсов.
        parser (CbrXmlParser): Парсер для XML-ответов ЦБ.
    """

    url = "http://www.cbr.ru/scripts/XML_daily.asp"
    DEFAULT_BASE_CURRENCY = "RUB"

    def __init__(self, base_currency: str = DEFAULT_BASE_CURRENCY):
        """Инициализировать клиент API ЦБ РФ.

        Аргументы:
            base_currency (str): Код базовой валюты (например, 'USD', 'EUR'). По умолчанию 'RUB'.
        """
        self.base_currency = base_currency.upper()
        self.client = ApiClient()
        self.cache = CacheManager()
        self.parser = XmlParser()

    async def _fetch_rates(self) -> Dict[str, Decimal]:
        """Получить и распарсить курсы валют от API ЦБ.

        Возвращает:
            Dict[str, Decimal]: Курсы валют относительно RUB.

        Исключения:
            httpx.HTTPStatusError: Если запрос к API завершился ошибкой.
        """
        response = await self.client.get(self.url)
        return self.parser.parse(response.text)

    async def _get_all_rates(self) -> Dict[str, Decimal]:
        """Получить все курсы валют, пересчитанные относительно базовой валюты.

        Извлекает курсы из кэша или запрашивает их, если кэш пуст, затем
        пересчитывает их относительно заданной базовой валюты.

        Возвращает:
            Dict[str, Decimal]: Курсы валют относительно базовой валюты.

        Исключения:
            ValueError: Если базовая валюта не найдена в данных ЦБ.
        """
        if "rates" not in self.cache:
            self.cache.set("rates", await self._fetch_rates())
        rub_rates = self.cache.get("rates")

        if self.base_currency not in rub_rates:
            raise ValueError(
                f"Базовая валюта {self.base_currency} не найдена в данных ЦБ"
            )

        base_rate = rub_rates[self.base_currency]
        adjusted_rates = {code: rate / base_rate for code, rate in rub_rates.items()}
        return adjusted_rates

    async def get_currency_rate(self, currency_code: str) -> Decimal:
        """Получить курс указанной валюты относительно базовой валюты.

        Аргументы:
            currency_code (str): Код валюты (например, 'USD', 'EUR').

        Возвращает:
            Decimal: Курс валюты с точностью до 5 знаков после запятой.

        Исключения:
            ValueError: Если валюта не найдена в данных ЦБ.
        """
        getcontext().prec = 5
        rates = await self._get_all_rates()
        if currency_code not in rates:
            raise ValueError(f"Валюта {currency_code} не найдена")
        return rates[currency_code]

    async def exchange(
        self, from_currency: str, to_currency: str, amount: Decimal
    ) -> Decimal:
        """Конвертировать сумму из одной валюты в другую.

        Аргументы:
            from_currency (str): Код валюты, из которой конвертируем (например, 'USD').
            to_currency (str): Код валюты, в которую конвертируем (например, 'EUR').
            amount (Decimal): Сумма для конвертации.

        Возвращает:
            Decimal: Сконвертированная сумма с точностью до 5 знаков после запятой.

        Исключения:
            ValueError: Если одна из валют не найдена в данных ЦБ.
        """
        getcontext().prec = 5
        rates = await self._get_all_rates()
        if from_currency not in rates or to_currency not in rates:
            raise ValueError(
                f"Одна из валют ({from_currency}, {to_currency}) не найдена"
            )
        from_rate = rates[from_currency]
        to_rate = rates[to_currency]
        return (
            (from_rate / to_rate) * amount if from_currency != to_currency else amount
        )

    async def __aenter__(self):
        """Вход в асинхронный контекстный менеджер.

        Возвращает:
            CrbCurrencyAPI: Экземпляр клиента API.
        """
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Выход из асинхронного контекстного менеджера и закрытие HTTP-клиента.

        Аргументы:
            exc_type: Тип исключения (если есть).
            exc_val: Значение исключения (если есть).
            exc_tb: Трассировка исключения (если есть).
        """
        await self.client.__aexit__(exc_type, exc_val, exc_tb)
