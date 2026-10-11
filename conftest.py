"""Изоляция тестов от сети, файлов пользователя и активного часового пояса."""
import pytest
import requests
from django.utils import timezone


def pytest_addoption(parser):
    parser.addoption('--shuffle-seed', type=int, default=None,
                     help='Перемешать тесты воспроизводимо для проверки независимости')


def pytest_collection_modifyitems(items, config):
    for item in items:
        if not any(item.get_closest_marker(name) for name in ('unit', 'integration', 'scenario')):
            category = 'unit' if item.path.name in {
                'test_api_services.py', 'test_validators_param.py'
            } else 'integration'
            item.add_marker(getattr(pytest.mark, category))
    seed = config.getoption('--shuffle-seed')
    if seed is not None:
        import random
        random.Random(seed).shuffle(items)


@pytest.fixture(autouse=True)
def isolated_environment(monkeypatch, settings, tmp_path):
    # Настоящий HTTP запрещён. Интеграционные тесты заменяют эту заглушку своей.
    def unavailable_http(*args, **kwargs):
        response = requests.Response()
        response.status_code = 503
        response._content = b'{}'
        return response

    monkeypatch.setattr(requests.sessions.Session, 'send', unavailable_http)
    settings.MEDIA_ROOT = tmp_path / 'media'
    settings.OPENWEATHER_API_KEY = ''
    previous = timezone.get_current_timezone()
    timezone.deactivate()
    yield
    timezone.activate(previous)
