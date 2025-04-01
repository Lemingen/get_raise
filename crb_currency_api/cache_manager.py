from cachetools import TTLCache
from datetime import datetime, timedelta

class CacheManager:
    """Класс для управления кэшем с динамическим TTL в зависимости от выходных."""

    def __init__(self, maxsize: int = 100):
        """Инициализирует кэш с заданным максимальным размером."""
        self.cache = TTLCache(maxsize=maxsize, ttl=self._calculate_ttl())

    def _calculate_ttl(self) -> int:
        """Вычисляет TTL в секундах до следующего рабочего дня."""
        now = datetime.now()
        weekday = now.weekday()  # 0 = понедельник, 6 = воскресенье

        if weekday < 4:  # Понедельник-четверг
            # До следующего дня (00:00 следующего дня)
            next_update = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        elif weekday == 4:  # Пятница
            # До понедельника (00:00 понедельника)
            next_update = (now + timedelta(days=3)).replace(hour=0, minute=0, second=0, microsecond=0)
        else:  # Суббота или воскресенье
            # До понедельника
            days_to_monday = 7 - weekday if weekday == 6 else 1
            next_update = (now + timedelta(days=days_to_monday)).replace(hour=0, minute=0, second=0, microsecond=0)

        ttl = int((next_update - now).total_seconds())
        return max(ttl, 1)  # Минимальный TTL — 1 секунда

    def get(self, key: str):
        """Получает значение из кэша."""
        return self.cache.get(key)

    def set(self, key: str, value):
        """Сохраняет значение в кэш с обновлённым TTL."""
        self.cache = TTLCache(maxsize=self.cache.maxsize, ttl=self._calculate_ttl())
        self.cache[key] = value

    def __contains__(self, key: str) -> bool:
        """Проверяет, есть ли ключ в кэше."""
        return key in self.cache