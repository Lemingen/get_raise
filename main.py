import asyncio
from decimal import Decimal
from crb_currency_api import CrbCurrencyAPI


async def main():
    """Демонстрирует использование CrbCurrencyAPI с разными базовыми валютами."""
    # Пример с базовой валютой RUB (по умолчанию)
    async with CrbCurrencyAPI() as api:
        eur_rate = await api.get_currency_rate("EUR")
        print(f"1 EUR = {eur_rate} RUB")
        usd_to_eur = await api.exchange("USD", "EUR", Decimal("100"))
        print(f"100 USD = {usd_to_eur} EUR")

    # Пример с базовой валютой USD
    async with CrbCurrencyAPI(base_currency="USD") as api:
        eur_rate = await api.get_currency_rate("EUR")
        print(f"1 EUR = {eur_rate} USD")
        eur_to_gbp = await api.exchange("EUR", "GBP", Decimal("100"))
        print(f"100 EUR = {eur_to_gbp} GBP")

    # Пример с базовой валютой EUR
    async with CrbCurrencyAPI(base_currency="EUR") as api:
        gbp_rate = await api.get_currency_rate("GBP")
        print(f"1 GBP = {gbp_rate} EUR")
        usd_to_gbp = await api.exchange("USD", "GBP", Decimal("100"))
        print(f"100 USD = {usd_to_gbp} GBP")

    async with CrbCurrencyAPI() as api:
        usd_to_rud = await api.exchange("USD", "RUB", Decimal("1"))
        print(f"1 USD = {usd_to_rud} RUB")


if __name__ == "__main__":
    asyncio.run(main())