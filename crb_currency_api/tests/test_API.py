import pytest
import httpx
from decimal import Decimal
from crb_currency_api.api import CrbCurrencyAPI

# Пример XML-ответа от ЦБ для тестов (упрощенный)
MOCK_XML_RESPONSE = """
<ValCurs Date="28.03.2025" name="Foreign Currency Market">
    <Valute ID="R01235">
        <NumCode>840</NumCode>
        <CharCode>USD</CharCode>
        <Nominal>1</Nominal>
        <Name>Доллар США</Name>
        <Value>92,3050</Value>
        <VunitRate>92,3050</VunitRate>
    </Valute>
    <Valute ID="R01239">
        <NumCode>978</NumCode>
        <CharCode>EUR</CharCode>
        <Nominal>1</Nominal>
        <Name>Евро</Name>
        <Value>100,1234</Value>
        <VunitRate>100,1234</VunitRate>
    </Valute>
    <Valute ID="R01090">
        <NumCode>826</NumCode>
        <CharCode>GBP</CharCode>
        <Nominal>1</Nominal>
        <Name>Фунт стерлингов</Name>
        <Value>116,7890</Value>
        <VunitRate>116,7890</VunitRate>
    </Valute>
</ValCurs>
"""

@pytest.fixture
async def mock_api(monkeypatch):
    """
    Фикстура для создания экземпляра CrbCurrencyAPI с замоканным HTTP-клиентом.

    Args:
        monkeypatch: Объект monkeypatch для замены атрибутов.

    Yields:
        CrbCurrencyAPI: Экземпляр API с замоканным HTTP-клиентом.
    """
    api = CrbCurrencyAPI()
    # Мокаем метод _make_request с помощью monkeypatch
    async def mock_make_request(url):
        """
        Замоканная функция для имитации HTTP-запроса.

        Args:
            url (str): URL запроса (не используется в моке).

        Returns:
            httpx.Response: Замоканный HTTP-ответ с данными из MOCK_XML_RESPONSE.
        """
        return httpx.Response(200, text=MOCK_XML_RESPONSE)
    monkeypatch.setattr(api, "_make_request", mock_make_request)
    yield api
    await api.client.aclose()  # Закрываем клиент после теста

@pytest.mark.asyncio
async def test_get_currency_rate_default_base_rub(mock_api):
    """
    Тест получения курса валюты с базовой валютой RUB.

    Args:
        mock_api: Фикстура API с замоканным HTTP-клиентом.
    """
    rate = await mock_api.get_currency_rate("USD")
    assert rate == Decimal("92.3050")  # Проверяем курс USD/RUB из мок-ответа

@pytest.mark.asyncio
async def test_get_currency_rate_custom_base_usd(monkeypatch):
    """
    Тест получения курса валюты с базовой валютой USD.

    Args:
        monkeypatch: Объект monkeypatch для замены атрибутов.
    """
    api = CrbCurrencyAPI(base_currency="USD")
    async def mock_make_request(url):
        """
        Замоканная функция для имитации HTTP-запроса.

        Args:
            url (str): URL запроса (не используется в моке).

        Returns:
            httpx.Response: Замоканный HTTP-ответ с данными из MOCK_XML_RESPONSE.
        """
        return httpx.Response(200, text=MOCK_XML_RESPONSE)
    monkeypatch.setattr(api, "_make_request", mock_make_request)

    rate = await api.get_currency_rate("EUR")
    expected_rate = Decimal("100.1234") / Decimal("92.3050")  # EUR/RUB ÷ USD/RUB
    assert rate == pytest.approx(expected_rate, abs=Decimal("0.00001"))  # Проверка с учетом округления

@pytest.mark.asyncio
async def test_get_currency_rate_unknown_currency(mock_api):
    """
    Тест получения курса для неизвестной валюты.

    Args:
        mock_api: Фикстура API с замоканным HTTP-клиентом.
    """
    with pytest.raises(ValueError, match="Валюта XYZ не найдена"):
        await mock_api.get_currency_rate("XYZ")

@pytest.mark.asyncio
async def test_exchange_rub_base(mock_api):
    """
    Тест конвертации валют с базовой валютой RUB.

    Args:
        mock_api: Фикстура API с замоканным HTTP-клиентом.
    """
    amount = await mock_api.exchange("USD", "EUR", Decimal("100"))
    usd_rate = Decimal("92.3050")  # USD/RUB
    eur_rate = Decimal("100.1234")  # EUR/RUB
    expected_amount = (usd_rate / eur_rate) * Decimal("100")
    assert amount == pytest.approx(expected_amount, abs=Decimal("0.00001"))

@pytest.mark.asyncio
async def test_exchange_custom_base_usd(monkeypatch):
    """
    Тест конвертации валют с базовой валютой USD.

    Args:
        monkeypatch: Объект monkeypatch для замены атрибутов.
    """
    api = CrbCurrencyAPI(base_currency="USD")
    async def mock_make_request(url):
        """
        Замоканная функция для имитации HTTP-запроса.

        Args:
            url (str): URL запроса (не используется в моке).

        Returns:
            httpx.Response: Замоканный HTTP-ответ с данными из MOCK_XML_RESPONSE.
        """
        return httpx.Response(200, text=MOCK_XML_RESPONSE)
    monkeypatch.setattr(api, "_make_request", mock_make_request)

    amount = await api.exchange("EUR", "GBP", Decimal("100"))
    eur_rate = Decimal("100.1234") / Decimal("92.3050")  # EUR/USD
    gbp_rate = Decimal("116.7890") / Decimal("92.3050")  # GBP/USD
    expected_amount = (eur_rate / gbp_rate) * Decimal("100")
    assert amount == pytest.approx(expected_amount, abs=Decimal("0.00001"))

@pytest.mark.asyncio
async def test_exchange_same_currency(mock_api):
    """
    Тест конвертации в ту же валюту.

    Args:
        mock_api: Фикстура API с замоканным HTTP-клиентом.
    """
    amount = await mock_api.exchange("USD", "USD", Decimal("100"))
    assert amount == Decimal("100")  # Если валюты одинаковые, сумма не меняется

@pytest.mark.asyncio
async def test_invalid_base_currency(monkeypatch):
    """
    Тест создания API с некорректной базовой валютой.

    Args:
        monkeypatch: Объект monkeypatch для замены атрибутов.
    """
    api = CrbCurrencyAPI(base_currency="XYZ")
    async def mock_make_request(url):
        """
        Замоканная функция для имитации HTTP-запроса.

        Args:
            url (str): URL запроса (не используется в моке).

        Returns:
            httpx.Response: Замоканный HTTP-ответ с данными из MOCK_XML_RESPONSE.
        """
        return httpx.Response(200, text=MOCK_XML_RESPONSE)
    monkeypatch.setattr(api, "_make_request", mock_make_request)

    with pytest.raises(ValueError, match="Базовая валюта XYZ не найдена в данных ЦБ"):
        await api.get_currency_rate("USD")

@pytest.mark.asyncio
async def test_cache_usage(mock_api, monkeypatch):
    """
    Тест использования кэша для повторных запросов.

    Args:
        mock_api: Фикстура API с замоканным HTTP-клиентом.
        monkeypatch: Объект monkeypatch для замены атрибутов.
    """
    # Первый запрос
    rate1 = await mock_api.get_currency_rate("USD")
    assert rate1 == Decimal("92.3050")

    # Мокаем _make_request, чтобы проверить, что он не вызывается повторно
    call_count = 0
    async def mock_make_request(url):
        """
        Замоканная функция для имитации HTTP-запроса и подсчета вызовов.

        Args:
            url (str): URL запроса (не используется в моке).

        Returns:
            httpx.Response: Замоканный HTTP-ответ с данными из MOCK_XML_RESPONSE.
        """
        nonlocal call_count
        call_count += 1
        return httpx.Response(200, text=MOCK_XML_RESPONSE)
    monkeypatch.setattr(mock_api, "_make_request", mock_make_request)

    # Второй запрос должен использовать кэш
    rate2 = await mock_api.get_currency_rate("USD")
    assert rate2 == Decimal("92.3050")
    assert call_count == 0  # Проверяем, что запрос не делался благодаря кэшу