from abc import ABC, abstractmethod
from decimal import Decimal
from tenacity import retry, stop_after_attempt, retry_if_exception, wait_fixed
import httpx
from cachetools import TTLCache

class BaseAPI(ABC):
    """Абстрактный базовый класс для работы с API курсов валют.

    Предоставляет общую логику для выполнения HTTP-запросов, кэширования и повторных попыток.
    """

    RETRIES = 3
    RETRY_STATUS_CODES = [429, 500, 502, 503, 504]

    def __init__(self):
        """Инициализирует объект BaseAPI с кэшем и HTTP-клиентом."""
        self.cache = TTLCache(maxsize=100, ttl=86400)  # Кеш на 24 часа
        self.client = httpx.AsyncClient(timeout=10.0)  # Асинхронный клиент с таймаутом 10 секунд

    @abstractmethod
    async def get_currency_rate(self, currency_code: str) -> Decimal:
        """Абстрактный метод для получения курса валюты.

        Args:
            currency_code (str): Код валюты (например, 'USD', 'EUR').

        Returns:
            Decimal: Курс валюты относительно базовой валюты.

        Raises:
            NotImplementedError: Если метод не реализован в дочернем классе.
        """
        pass

    def _should_retry(self, exc: BaseException) -> bool:
        """Проверяет, нужно ли повторить запрос при возникновении ошибки.

        Args:
            exc (BaseException): Исключение, возникшее при запросе.

        Returns:
            bool: True, если запрос нужно повторить, иначе False.
        """
        if isinstance(exc, httpx.HTTPStatusError):
            return exc.response.status_code in self.RETRY_STATUS_CODES
        return False

    @retry(
        stop=stop_after_attempt(RETRIES),
        wait=wait_fixed(2),
        retry=retry_if_exception(_should_retry)
    )
    async def _make_request(self, url: str) -> httpx.Response:
        """Выполняет асинхронный HTTP-запрос с повторными попытками.

        Args:
            url (str): Адрес API для запроса.

        Returns:
            httpx.Response: Ответ сервера.

        Raises:
            httpx.HTTPStatusError: Если запрос завершился с ошибкой после всех попыток.
        """
        response = await self.client.get(url)
        response.raise_for_status()
        return response

    async def __aenter__(self):
        """Поддержка асинхронного контекстного менеджера (вход).

        Returns:
            BaseAPI: Экземпляр класса.
        """
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Поддержка асинхронного контекстного менеджера (выход).

        Закрывает HTTP-клиент при завершении работы.

        Args:
            exc_type: Тип исключения (если есть).
            exc_val: Значение исключения (если есть).
            exc_tb: Трассировка исключения (если есть).
        """
        await self.client.aclose()