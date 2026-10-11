"""Реальная цепочка Client → view → service → requests; заглушка только транспорта."""
import json
import pytest
import requests
from django.urls import reverse

pytestmark = [pytest.mark.django_db, pytest.mark.integration]


def install_http_stub(monkeypatch, payloads, status=200, error=None):
    calls = []

    def send(session, request, **kwargs):
        calls.append((request, kwargs))
        if error:
            raise error
        response = requests.Response()
        response.status_code = status
        response._content = json.dumps(payloads['currency' if 'nbrb.by' in request.url else 'weather']).encode()
        response.request = request
        return response

    monkeypatch.setattr(requests.sessions.Session, 'send', send)
    return calls


def test_datetime_page_parses_both_external_services_at_http_boundary(client, monkeypatch, settings):
    # Arrange
    settings.OPENWEATHER_API_KEY = 'stub-key'
    currencies = [{'Cur_Abbreviation': code, 'Cur_Name': code, 'Cur_OfficialRate': 3,
                   'Cur_Scale': 100 if code == 'RUB' else 1, 'Date': '2026-10-11'}
                  for code in ('USD', 'EUR', 'RUB', 'PLN', 'JPY')]
    weather = {'name': 'Minsk', 'main': {'temp': 15.5, 'feels_like': 14, 'temp_min': 12,
                'temp_max': 18, 'humidity': 60, 'pressure': 1000}, 'wind': {'speed': 3.5},
               'weather': [{'description': 'ясно', 'icon': '01d'}], 'clouds': {'all': 20},
               'visibility': 10000}
    calls = install_http_stub(monkeypatch, {'currency': currencies, 'weather': weather})
    # Act
    response = client.get(reverse('core:datetime_demo'))
    # Assert
    assert response.status_code == 200
    assert set(response.context['currency_rates']) == {'USD', 'EUR', 'RUB', 'PLN'}
    assert response.context['currency_rates']['RUB']['scale'] == 100
    assert response.context['weather']['temperature'] == 16
    assert response.context['weather']['pressure'] == 750
    assert response.context['weather']['visibility'] == 10
    assert len(calls) == 2
    assert all(request.method == 'GET' and kwargs['timeout'] == 10 for request, kwargs in calls)
    assert 'q=Minsk,BY' in calls[1][0].url and 'appid=stub-key' in calls[1][0].url


@pytest.mark.parametrize('status,error,payload', [
    (503, None, {}), (200, requests.Timeout('timeout'), {}),
])
def test_datetime_page_survives_external_http_failures(client, monkeypatch, settings, status, error, payload):
    # Arrange
    settings.OPENWEATHER_API_KEY = 'stub-key'
    calls = install_http_stub(monkeypatch, {'currency': payload, 'weather': payload}, status, error)
    # Act
    response = client.get(reverse('core:datetime_demo'))
    # Assert
    assert response.status_code == 200
    assert response.context['currency_rates'] is None
    assert response.context['weather'] is None
    assert len(calls) == 2
