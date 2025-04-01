from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Dict
from xml.etree import ElementTree

class Parser(ABC):
    """Абстрактный базовый класс для парсинга данных API."""

    @abstractmethod
    def parse(self, response_text: str) -> Dict[str, Decimal]:
        """Парсит данные из ответа API."""
        pass

class CbrXmlParser(Parser):
    """Парсер для XML-ответов от ЦБ РФ."""

    def parse(self, response_text: str) -> Dict[str, Decimal]:
        """Парсит XML от ЦБ и возвращает курсы валют относительно рубля."""
        root = ElementTree.fromstring(response_text)
        rates = {"RUB": Decimal("1.0")}
        for currency in root.findall("Valute"):
            try:
                code = currency.find("CharCode").text
                rate = currency.find("VunitRate").text.replace(",", ".")
                rates[code] = Decimal(rate)
            except (AttributeError, ValueError) as e:
                print(f"Ошибка парсинга валюты: {e}")
        return rates