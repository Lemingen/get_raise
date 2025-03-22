import asyncio
from decimal import Decimal
import httpx
from abc import ABC, abstractmethod

class CurrencyProvider(ABC):
    @abstractmethod
    async def get_rates(self) -> dict:
        pass

class CBRProvider(CurrencyProvider):
    async def get_rates(self) -> dict:
        url = "https://www.cbr.ru/scripts/XML_daily.asp"
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=10)
                response.raise_for_status()
                return self.parse_xml(response.text)
        except (httpx.HTTPError, ValueError) as e:
            print(f"Error fetching CBR rates: {e}")
            return {}

    def parse_xml(self, xml_str: str) -> dict:
        # XML parsing logic goes here
        return {}

class AlternativeProvider(CurrencyProvider):
    async def get_rates(self) -> dict:
        url = "https://api.alternative.com/rates"
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=10)
                response.raise_for_status()
                return self.parse_json(response.json())
        except (httpx.HTTPError, ValueError) as e:
            print(f"Error fetching alternative rates: {e}")
            return {}

    def parse_json(self, json_data: dict) -> dict:
        # JSON parsing logic goes here
        return {}

async def get_currency_rates():
    providers = [CBRProvider(), AlternativeProvider()]
    for provider in providers:
        rates = await provider.get_rates()
        if rates:
            return {k: Decimal(str(v)) for k, v in rates.items()}
    return {}

async def main():
    rates = await get_currency_rates()
    print(rates)

if __name__ == "__main__":
    asyncio.run(main())
