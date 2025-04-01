from decimal import Decimal, getcontext
from typing import Dict
from crb_currency_api.baseAPI import BaseAPI
from crb_currency_api.api_client import ApiClient
from crb_currency_api.cache_manager import CacheManager
from crb_currency_api.parsers import CbrXmlParser

class CrbCurrencyAPI(BaseAPI):
    """Класс для работы с API ЦБ РФ с разделёнными ответственностями."""

    url = "http://www.cbr.ru/scripts/XML_daily.asp"
    DEFAULT_BASE_CURRENCY = "RUB"

    def __init__(self, base_currency: str = DEFAULT_BASE_CURRENCY):
        self.base_currency = base_currency.upper()
        self.client = ApiClient()
        self.cache = CacheManager()
        self.parser = CbrXmlParser()

    async def _fetch_rates(self) -> Dict[str, Decimal]:
        """Получает и парсит курсы валют от ЦБ."""
        response = await self.client.get(self.url)
        return self.parser.parse(response.text)

    async def _get_all_rates(self) -> Dict[str, Decimal]:
        """Возвращает курсы валют относительно базовой валюты."""
        if "rates" not in self.cache:
            self.cache.set("rates", await self._fetch_rates())
        rub_rates = self.cache.get("rates")

        if self.base_currency not in rub_rates:
            raise ValueError(f"Базовая валюта {self.base_currency} не найдена")

        base_rate = rub_rates[self.base_currency]
        adjusted_rates = {code: rate / base_rate for code, rate in rub_rates.items()}
        return adjusted_rates

    async def get_currency_rate(self, currency_code: str) -> Decimal:
        """Получает курс валюты."""
        getcontext().prec = 5
        rates = await self._get_all_rates()
        if currency_code not in rates:
            raise ValueError(f"Валюта {currency_code} не найдена")
        return rates[currency_code]

    async def exchange(self, from_currency: str, to_currency: str, amount: Decimal) -> Decimal:
        """Конвертирует сумму между валютами."""
        getcontext().prec = 5
        rates = await self._get_all_rates()
        if from_currency not in rates or to_currency not in rates:
            raise ValueError(f"Одна из валют ({from_currency}, {to_currency}) не найдена")
        from_rate = rates[from_currency]
        to_rate = rates[to_currency]
        return (from_rate / to_rate) * amount if from_currency != to_currency else amount

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.__aexit__(exc_type, exc_val, exc_tb)