from decimal import Decimal

from Crb_currency_api.parsers import XmlParser


def test_cbr_xml_parser_success():
    """Тест успешного парсинга корректных XML-данных."""
    parser = XmlParser()
    xml_data = """
    <ValCurs>
        <Valute>
            <CharCode>USD</CharCode>
            <VunitRate>97.1234</VunitRate>
        </Valute>
        <Valute>
            <CharCode>EUR</CharCode>
            <VunitRate>102.5678</VunitRate>
        </Valute>
    </ValCurs>
    """
    rates = parser.parse(xml_data)
    assert rates["RUB"] == Decimal("1.0")
    assert rates["USD"] == Decimal("97.1234")
    assert rates["EUR"] == Decimal("102.5678")


def test_cbr_xml_parser_invalid_data():
    """Тест обработки XML с пустым значением VunitRate (вызывает ValueError)."""
    parser = XmlParser()
    xml_data = """
    <ValCurs>
        <Valute>
            <CharCode>USD</CharCode>
            <VunitRate></VunitRate>
        </Valute>
    </ValCurs>
    """
    rates = parser.parse(xml_data)
    assert rates == {"RUB": Decimal("1.0")}  # Только RUB, USD пропущен из-за ошибки
    assert "USD" not in rates  # Убеждаемся, что некорректная валюта исключена