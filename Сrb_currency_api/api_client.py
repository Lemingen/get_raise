import httpx
from tenacity import retry, stop_after_attempt, retry_if_exception, wait_fixed

class ApiClient:
    """Асинхронный HTTP-клиент для выполнения запросов к API с повторными попытками.

    Обрабатывает GET-запросы с настраиваемыми повторными попытками для определённых
    кодов состояния (например, ограничение скорости или ошибки сервера).

    Атрибуты:
        RETRIES (int): Количество попыток повтора (по умолчанию: 3).
        RETRY_STATUS_CODES (list): Коды состояния HTTP, при которых выполняются повторы (например, 429, 500).
        client (httpx.AsyncClient): Внутренний HTTP-клиент.
    """

    RETRIES = 3
    RETRY_STATUS_CODES = [429, 500, 502, 503, 504]

    def __init__(self, timeout: float = 10.0):
        """Инициализировать клиент API с заданным таймаутом.

        Аргументы:
            timeout (float): Таймаут запроса в секундах (по умолчанию: 10.0).
        """
        self.client = httpx.AsyncClient(timeout=timeout)

    def _should_retry(self, exc: BaseException) -> bool:
        """Определить, нужно ли повторить запрос на основе возникшего исключения.

        Аргументы:
            exc (BaseException): Исключение, возникшее во время запроса.

        Возвращает:
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
    async def get(self, url: str) -> httpx.Response:
        """Выполнить асинхронный GET-запрос с повторными попытками.

        Аргументы:
            url (str): URL для запроса.

        Возвращает:
            httpx.Response: Ответ от сервера.

        Исключения:
            httpx.HTTPStatusError: Если запрос завершился ошибкой после всех попыток.
        """
        response = await self.client.get(url)
        response.raise_for_status()
        return response

    async def __aenter__(self):
        """Вход в асинхронный контекстный менеджер.

        Возвращает:
            ApiClient: Экземпляр клиента.
        """
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Выход из асинхронного контекстного менеджера и закрытие HTTP-клиента.

        Аргументы:
            exc_type: Тип исключения (если есть).
            exc_val: Значение исключения (если есть).
            exc_tb: Трассировка исключения (если есть).
        """
        await self.client.aclose()