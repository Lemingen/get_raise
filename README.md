# CrbCurrencyAPI

Библиотека на Python для получения и конвертации курсов валют от Центрального банка России (ЦБ РФ).

Этот проект предоставляет асинхронный клиент API, который запрашивает ежедневные курсы валют от ЦБ, парсит XML-ответы и поддерживает произвольные базовые валюты с кэшированием, учитывающим выходные дни.

## Возможности
- Асинхронные HTTP-запросы с повторными попытками для надёжности.
- Модульная архитектура с разделением запросов, парсинга и кэширования.
- Динамическое истечение кэша: до полуночи следующего рабочего дня (понедельник для выходных).
- Конвертация валют между любыми поддерживаемыми валютами.
- Расширяемая структура для добавления новых API или парсеров.

## Установка

1. **Клонируйте репозиторий**:
   ```bash
   git clone https://github.com/yourusername/crb-currency-api.git
   cd crb-currency-api
2. Установите зависимости:
```bash
pip install -r requirements.txt
Содержимое require.txt :
httpx
tenacity
cachetools

Использование
Основной класс CrbRequestCurrencyApi Позволяет получать курсы валют и 
осуществлять конверсию. Пример:
import asyncio
from decimal import Decimal
from crb_currency_api.crb_currency_api import CrbRequestCurrencyApi

async def example():
    async with CrbRequestCurrencyApi(base_currency="USD") as api:
        eur_rate = await api.get_currency_rate("EUR")
        print(f"1 EUR = {eur_rate} USD")
        usd_to_eur = await api.exchange("USD", "EUR", Decimal("100"))
        print(f"100 USD = {usd_to_eur} EUR")

if __name__ == "__main__":
    asyncio.run(example())
    
Дополнительные примеры с различными базовыми валютами см. в 
crb_currency_api/main.py .   
 

 