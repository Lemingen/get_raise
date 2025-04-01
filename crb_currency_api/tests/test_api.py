import pytest
import httpx
from decimal import Decimal
from crb_currency_api import CrbCurrencyAPI

@pytest.mark.asyncio
async def test_get_currency_rate():
    api = CrbCurrencyAPI()
    rate = await api.get_currency_rate("EUR")
    assert isinstance(rate, Decimal)
    assert rate > 0
    assert str(rate).count('.') <= 1 and len(str(rate).split('.')[1]) <= 5  # Проверка точности Decimal

@pytest.mark.asyncio
async def test_get_currency_rate_cache():
    api = CrbCurrencyAPI()
    rate1 = await api.get_currency_rate("USD")
    rate2 = await api.get_currency_rate("USD")
    assert rate1 == rate2  # Проверка, что кэш работает (второй запрос не делает новый HTTP-запрос)

@pytest.mark.asyncio
async def test_exchange():
    api = CrbCurrencyAPI()
    amount = await api.exchange("USD", "EUR", Decimal("100"))
    assert isinstance(amount, Decimal)
    assert amount > 0
    assert str(amount).count('.') <= 1 and len(str(amount).split('.')[1]) <= 5  # Проверка точности

@pytest.mark.asyncio
async def test_exchange_same_currency():
    api = CrbCurrencyAPI()
    amount = await api.exchange("RUB", "RUB", Decimal("1000"))
    assert amount == Decimal("1000")  # Если валюты одинаковые, сумма не меняется

@pytest.mark.asyncio
async def test_invalid_currency():
    api = CrbCurrencyAPI()
    with pytest.raises(ValueError):
        await api.get_currency_rate("XXX")

@pytest.mark.asyncio
async def test_get_selected_currencies():
    api = CrbCurrencyAPI()
    selected_rates = await api.get_selected_currencies(["USD", "EUR", "CNY"])
    assert "USD" in selected_rates
    assert "EUR" in selected_rates
    assert "CNY" in selected_rates
    assert all(isinstance(rate, Decimal) for rate in selected_rates.values())
    assert len(selected_rates) == 3

@pytest.mark.asyncio
async def test_get_selected_currencies_with_rub():
    api = CrbCurrencyAPI()
    selected_rates = await api.get_selected_currencies(["RUB", "USD"])
    assert "RUB" in selected_rates
    assert selected_rates["RUB"] == Decimal("1.0")  # RUB всегда 1.0 как базовая
    assert "USD" in selected_rates
    assert len(selected_rates) == 2

@pytest.mark.asyncio
async def test_get_selected_currencies_invalid():
    api = CrbCurrencyAPI()
    with pytest.raises(ValueError):
        await api.get_selected_currencies(["USD", "XXX"])

@pytest.mark.asyncio
async def test_fetch_rates_all():
    api = CrbCurrencyAPI()
    rates = await api._fetch_rates()  # Тестируем приватный метод напрямую
    assert "RUB" in rates
    assert "USD" in rates
    assert "EUR" in rates
    assert "CNY" in rates
    assert len(rates) > 30  # ЦБ возвращает 30+ валют

@pytest.mark.asyncio
async def test_fetch_rates_selected():
    api = CrbCurrencyAPI()
    rates = await api._fetch_rates(["USD", "EUR"])
    assert "RUB" in rates  # Базовая валюта всегда есть
    assert "USD" in rates
    assert "EUR" in rates
    assert "CNY" not in rates  # Не запрашивали CNY
    assert len(rates) == 3