from datetime import datetime

from Сrb_currency_api.cache_manager import CacheManager


def test_cache_manager_set_get():
    """Тест базовой работы кэша: установка и получение значения."""
    cache = CacheManager(maxsize=10)
    cache.set("key", "value")
    assert cache.get("key") == "value"
    assert "key" in cache


def test_cache_manager_ttl_weekday(monkeypatch):
    """Тест расчёта TTL для буднего дня (среда)."""
    # Мокаем дату: среда, 12:00
    class MockDateTime:
        @staticmethod
        def now():
            return datetime(2023, 10, 18, 12, 0, 0)  # Среда
    monkeypatch.setattr("Сrb_currency_api.cache_manager.datetime", MockDateTime)

    cache = CacheManager()
    ttl = cache._calculate_ttl()
    assert ttl == 12 * 3600  # 12 часов до полуночи четверга (00:00 следующего дня)


def test_cache_manager_ttl_friday(monkeypatch):
    """Тест расчёта TTL для пятницы с переходом на понедельник."""
    # Мокаем дату: пятница, 12:00
    class MockDateTime:
        @staticmethod
        def now():
            return datetime(2023, 10, 20, 12, 0, 0)  # Пятница
    monkeypatch.setattr("Сrb_currency_api.cache_manager.datetime", MockDateTime)

    cache = CacheManager()
    ttl = cache._calculate_ttl()
    assert ttl == 60 * 3600  # 60 часов до полуночи понедельника (от пятницы 12:00 до понедельника 00:00)