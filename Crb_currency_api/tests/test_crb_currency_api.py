from decimal import Decimal
from unittest.mock import AsyncMock

import pytest

from Crb_currency_api.crb_currency_api import CrbRequestCurrencyApi


@pytest.mark.asyncio
async def test_get_currency_rate_rub_base():
    api = CrbRequestCurrencyApi()
    mock_rates = {
        "RUB": Decimal("1.0"),
        "USD": Decimal("97.1234"),
        "EUR": Decimal("102.5678"),
    }
    api._fetch_rates = AsyncMock(return_value=mock_rates)

    rate = await api.get_currency_rate("USD")
    assert rate == Decimal("97.1234")
    assert api._fetch_rates.call_count == 1  # Проверяем кэширование
    rate_cached = await api.get_currency_rate("USD")  # noqa
    assert api._fetch_rates.call_count == 1  # Не вызвался снова


@pytest.mark.asyncio
async def test_get_currency_rate_usd_base():
    api = CrbRequestCurrencyApi(base_currency="USD")
    mock_rates = {
        "RUB": Decimal("1.0"),
        "USD": Decimal("97.1234"),
        "EUR": Decimal("102.5678"),
    }
    api._fetch_rates = AsyncMock(return_value=mock_rates)

    rate = await api.get_currency_rate("EUR")
    expected_rate = Decimal("102.5678") / Decimal("97.1234")
    assert rate == pytest.approx(expected_rate, abs=Decimal("0.00001"))


@pytest.mark.asyncio
async def test_exchange():
    api = CrbRequestCurrencyApi()
    mock_rates = {
        "RUB": Decimal("1.0"),
        "USD": Decimal("97.1234"),
        "EUR": Decimal("102.5678"),
    }
    api._fetch_rates = AsyncMock(return_value=mock_rates)

    result = await api.exchange("USD", "EUR", Decimal("100"))
    expected = (Decimal("97.1234") / Decimal("102.5678")) * Decimal("100")
    assert result == pytest.approx(expected, abs=Decimal("0.00001"))


@pytest.mark.asyncio
async def test_invalid_currency():
    api = CrbRequestCurrencyApi()
    mock_rates = {"RUB": Decimal("1.0"), "USD": Decimal("97.1234")}
    api._fetch_rates = AsyncMock(return_value=mock_rates)

    with pytest.raises(ValueError, match="Валюта XYZ не найдена"):
        await api.get_currency_rate("XYZ")


@pytest.mark.asyncio
async def test_context_manager():
    async with CrbRequestCurrencyApi() as api:
        assert isinstance(api, CrbRequestCurrencyApi)
        assert not api.client.client.is_closed
    assert api.client.client.is_closed
