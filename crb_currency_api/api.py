from typing import Dict
from crb_currency_api.baseApi import BaseAPI
from decimal import Decimal, getcontext
from xml.etree import ElementTree

class CrbCurrencyAPI(BaseAPI):
    """Класс для работы с API Центрального банка России для получения курсов валют.

    Поддерживает задание произвольной базовой валюты и пересчет курсов относительно неё.
    """

    url = "http://www.cbr.ru/scripts/XML_daily.asp"
    DEFAULT_BASE_CURRENCY = "RUB"  # Валюта по умолчанию — рубль

    def __init__(self, base_currency: str = DEFAULT_BASE_CURRENCY):
        """Инициализирует объект CrbCurrencyAPI с указанной базовой валютой.

        Args:
            base_currency (str, optional): Код базовой валюты (например, 'USD', 'EUR'). По умолчанию 'RUB'.
        """
        super().__init__()
        self.base_currency = base_currency.upper()  # Храним базовую валюту в верхнем регистре

    async def _fetch_rates(self) -> Dict[str, Decimal]:
        """Получает и парсит все курсы валют от ЦБ относительно рубля.

        Returns:
            Dict[str, Decimal]: Словарь с кодами валют и их курсами к рублю.

        Raises:
            httpx.HTTPStatusError: Если запрос к ЦБ завершился с ошибкой.
        """
        response = await self._make_request(self.url)
        root = ElementTree.fromstring(response.text)
        rates = {"RUB": Decimal("1.0")}  # Рубль всегда 1:1 к себе
        for currency in root.findall("Valute"):
            try:
                code = currency.find("CharCode").text
                rate = currency.find("VunitRate").text.replace(",", ".")
                rates[code] = Decimal(rate)
            except (AttributeError, ValueError) as e:
                print(f"Ошибка парсинга валюты: {e}")
        return rates

    async def _get_all_rates(self) -> Dict[str, Decimal]:
        """Возвращает курсы валют относительно текущей базовой валюты.

        Пересчитывает курсы, полученные от ЦБ (относительно RUB), в курсы относительно заданной базовой валюты.

        Returns:
            Dict[str, Decimal]: Словарь с кодами валют и их курсами к базовой валюте.

        Raises:
            ValueError: Если базовая валюта не найдена в данных ЦБ.
        """
        if "rates" not in self.cache:
            self.cache["rates"] = await self._fetch_rates()
        rub_rates = self.cache["rates"]

        if self.base_currency not in rub_rates:
            raise ValueError(f"Базовая валюта {self.base_currency} не найдена в данных ЦБ")

        base_rate = rub_rates[self.base_currency]  # Курс базовой валюты к рублю
        adjusted_rates = {}
        for code, rate in rub_rates.items():
            adjusted_rates[code] = rate / base_rate  # Пересчитываем относительно базовой валюты
        return adjusted_rates

    async def get_currency_rate(self, currency_code: str) -> Decimal:
        """Получает курс указанной валюты относительно текущей базовой валюты.

        Args:
            currency_code (str): Код валюты (например, 'USD', 'EUR').

        Returns:
            Decimal: Курс валюты с точностью до 5 знаков после запятой.

        Raises:
            ValueError: Если валюта не найдена в данных ЦБ.
        """
        getcontext().prec = 5
        rates = await self._get_all_rates()
        if currency_code not in rates:
            raise ValueError(f"Валюта {currency_code} не найдена")
        return rates[currency_code]

    async def exchange(self, from_currency: str, to_currency: str, amount: Decimal) -> Decimal:
        """Конвертирует сумму из одной валюты в другую относительно базовой валюты.

        Args:
            from_currency (str): Код валюты, из которой конвертируем (например, 'USD').
            to_currency (str): Код валюты, в которую конвертируем (например, 'EUR').
            amount (Decimal): Сумма для конвертации.

        Returns:
            Decimal: Сконвертированная сумма с точностью до 5 знаков после запятой.

        Raises:
            ValueError: Если одна из валют не найдена в данных ЦБ.
        """
        getcontext().prec = 5
        rates = await self._get_all_rates()
        if from_currency not in rates or to_currency not in rates:
            raise ValueError(f"Одна из валют ({from_currency}, {to_currency}) не найдена")
        from_rate = rates[from_currency]
        to_rate = rates[to_currency]
        return (from_rate / to_rate) * amount if from_currency != to_currency else amount