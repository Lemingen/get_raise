from cachetools import TTLCache
from datetime import datetime, timedelta

class CacheManager:
    """Менеджер кэша с динамическим TTL, учитывающим выходные дни.

    Управляет кэшем, устанавливая время жизни данных до полуночи следующего рабочего
    дня (понедельник для выходных, следующий день для будней).

    Атрибуты:
        cache (TTLCache): Внутренний объект кэша.
    """

    def __init__(self, maxsize: int = 100):
        """Инициализировать менеджер кэша с максимальным размером.

        Аргументы:
            maxsize (int): Максимальное количество элементов в кэше (по умолчанию: 100).
        """
        self.cache = TTLCache(maxsize=maxsize, ttl=self._calculate_ttl())

    def _calculate_ttl(self) -> int:
        """Рассчитать TTL в секундах до следующего рабочего дня.

        TTL устанавливается:
        - До полуночи следующего дня для понедельника-четверга.
        - До полуночи понедельника для пятницы-воскресенья.

        Возвращает:
            int: TTL в секундах.
        """
        now = datetime.now()
        weekday = now.weekday()  # 0 = понедельник, 6 = воскресенье

        if weekday < 4:  # Понедельник-четверг
            next_update = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        elif weekday == 4:  # Пятница
            next_update = (now + timedelta(days=3)).replace(hour=0, minute=0, second=0, microsecond=0)
        else:  # Суббота или воскресенье
            days_to_monday = 7 - weekday if weekday == 6 else 1
            next_update = (now + timedelta(days=days_to_monday)).replace(hour=0, minute=0, second=0, microsecond=0)

        ttl = int((next_update - now).total_seconds())
        return max(ttl, 1)  # Минимальный TTL — 1 секунда

    def get(self, key: str):
        """Получить значение из кэша.

        Аргументы:
            key (str): Ключ для поиска.

        Возвращает:
            Значение из кэша или None, если ключ не найден.
        """
        return self.cache.get(key)

    def set(self, key: str, value):
        """Сохранить значение в кэше с обновлённым TTL.

        Аргументы:
            key (str): Ключ для сохранения значения.
            value: Значение для кэширования.
        """
        self.cache = TTLCache(maxsize=self.cache.maxsize, ttl=self._calculate_ttl())
        self.cache[key] = value

    def __contains__(self, key: str) -> bool:
        """Проверить, существует ли ключ в кэше.

        Аргументы:
            key (str): Ключ для проверки.

        Возвращает:
            bool: True, если ключ существует, иначе False.
        """
        return key in self.cache