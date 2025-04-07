from unittest.mock import AsyncMock

import httpx
import pytest

from Crb_currency_api.api_client import ApiClient

@pytest.mark.asyncio
async def test_api_client_successful_request():
    client = ApiClient()

    # Создаём фейковый ответ с запросом, чтобы raise_for_status() не упал
    request = httpx.Request("GET", "http://test.url")
    mock_response = httpx.Response(status_code=200, text="OK", request=request)

    # Мокаем метод get
    client.client.get = AsyncMock(return_value=mock_response)

    # Тестируем
    response = await client.get("http://test.url")
    assert response.status_code == 200
    assert response.text == "OK"

@pytest.mark.asyncio
async def test_api_client_retry_on_failure():
    client = ApiClient()

    # Добавляем request в каждый мокнутый response
    request = httpx.Request("GET", "http://test.url")
    mock_response_429 = httpx.Response(429, text="Too Many Requests", request=request)
    mock_response_200 = httpx.Response(200, text="OK", request=request)

    # Первая попытка — ошибка, вторая — успех
    client.client.get = AsyncMock(side_effect=[mock_response_429, mock_response_200])

    # Тестируем
    response = await client.get("http://test.url")

    # Проверки
    assert response.status_code == 200
    assert response.text == "OK"
    assert client.client.get.call_count == 2

@pytest.mark.asyncio
async def test_api_client_context_manager():
    async with ApiClient() as client:
        assert isinstance(client, ApiClient)
        assert not client.client.is_closed
    assert client.client.is_closed