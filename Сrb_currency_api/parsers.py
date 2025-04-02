from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Dict
from xml.etree import ElementTree

class Parser(ABC):
    """Абстрактный базовый класс для парсинга ответов API.

    Дочерние классы должны реализовать метод parse для извлечения курсов валют.
    """

    @abstractmethod
    def parse(self, response_text: str) -> Dict[str, Decimal]:
        """Распарсить ответ API в словарь курсов валют.

        Аргументы:
            response_text (str): Необработанный текстовый ответ от API.

        Возвращает:
            Dict[str, Decimal]: Словарь, сопоставляющий коды валют их курсам.
        """
        pass


class XmlParser(Parser):
    """Парсер для XML-ответов API Центрального банка России.

    Извлекает курсы валют из ежедневного XML-фида ЦБ РФ.
    """

    def parse(self, response_text: str) -> Dict[str, Decimal]:
        """Распарсить XML-данные ЦБ в словарь курсов валют относительно RUB.

        Аргументы:
            response_text (str): Текст XML-ответа от API ЦБ.

        Возвращает:
            Dict[str, Decimal]: Коды валют и их курсы (RUB всегда 1.0).

        Исключения:
            AttributeError: Если структура XML некорректна.
            ValueError: Если парсинг курса завершился неудачей.
        """
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