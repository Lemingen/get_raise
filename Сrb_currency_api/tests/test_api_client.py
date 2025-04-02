from unittest.mock import AsyncMock

import httpx
import pytest

from Сrb_currency_api.api_client import ApiClient


@pytest.mark.asyncio
async def test_api_client_successful_request():
    client = ApiClient()
    mock_response = httpx.Response(200, text="OK")
    client.client.get = AsyncMock(return_value=mock_response)

    response = await client.get("http://test.url")
    assert response.status_code == 200
    assert response.text == "OK"

@pytest.mark.asyncio
async def test_api_client_retry_on_failure():
    client = ApiClient()
    mock_response_429 = httpx.Response(429, text="Too Many Requests")
    mock_response_200 = httpx.Response(200, text="OK")
    client.client.get = AsyncMock(side_effect=[mock_response_429, mock_response_200])

    response = await client.get("http://test.url")
    assert response.status_code == 200
    assert client.client.get.call_count == 2  # Проверяем, что была повторная попытка

@pytest.mark.asyncio
async def test_api_client_context_manager():
    async with ApiClient() as client:
        assert isinstance(client, ApiClient)
        assert not client.client.is_closed
    assert client.client.is_closed