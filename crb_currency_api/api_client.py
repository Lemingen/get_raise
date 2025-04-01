import httpx
from tenacity import retry, stop_after_attempt, retry_if_exception, wait_fixed

class ApiClient:
    """Класс для выполнения асинхронных HTTP-запросов с повторными попытками."""

    RETRIES = 3
    RETRY_STATUS_CODES = [429, 500, 502, 503, 504]

    def __init__(self, timeout: float = 10.0):
        """Инициализирует клиент с настройками таймаута."""
        self.client = httpx.AsyncClient(timeout=timeout)

    def _should_retry(self, exc: BaseException) -> bool:
        """Проверяет, нужно ли повторить запрос."""
        if isinstance(exc, httpx.HTTPStatusError):
            return exc.response.status_code in self.RETRY_STATUS_CODES
        return False

    @retry(
        stop=stop_after_attempt(RETRIES),
        wait=wait_fixed(2),
        retry=retry_if_exception(_should_retry)
    )
    async def get(self, url: str) -> httpx.Response:
        """Выполняет GET-запрос."""
        response = await self.client.get(url)
        response.raise_for_status()
        return response

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()