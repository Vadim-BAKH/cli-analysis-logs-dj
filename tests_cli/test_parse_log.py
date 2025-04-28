"""
Модуль тестов для функции parse_log_file из модуля logs_parser.

Проверяет корректность парсинга различных вариантов строк логов.
"""

from pathlib import Path

import pytest
from logs_analyzer.logs_parser import parse_log_file


@pytest.fixture
def create_log_file1(tmp_path: Path) -> callable:
    """
    Фикстура для создания временного лог-файла с заданным содержимым.

    :param tmp_path: Временная директория pytest
    :return: Функция, принимающая строку содержимого и
             возвращающая путь к созданному файлу.
    """
    def _create(content: str) -> Path:
        file = tmp_path / "test.log"
        file.write_text(content, encoding="utf-8")
        return file

    return _create


def test_parse_log_file_valid_line(create_log_file1):
    """Корректный парсинг одной валидной строки лога."""
    content = ("2025-03-28 12:44:46,000 INFO django.request:"
               " GET /api/v1/reviews/ 204 OK [192.168.1.59]\n")
    log_file = create_log_file1(content)
    records = parse_log_file(log_file)
    assert records == [{"handler": "/api/v1/reviews/", "level": "INFO"}]


def test_parse_log_file_multiple_lines(create_log_file1):
    """Парсинг строк с разными уровнями логирования."""
    content = (
        "2025-03-28 12:05:13,000 INFO django.request:"
        " GET /api/v1/reviews/ 201 OK [192.168.1.97]\n"
        "2025-03-28 12:11:57,000 ERROR django.request:"
        " Internal Server Error: /admin/dashboard/"
        " [192.168.1.29] - ValueError: Invalid input data\n"
    )
    log_file = create_log_file1(content)
    records = parse_log_file(log_file)
    assert records == [
        {"handler": "/api/v1/reviews/", "level": "INFO"},
        {"handler": "/admin/dashboard/", "level": "ERROR"},
    ]


def test_parse_log_file_with_unicode_and_spaces(create_log_file1):
    """Парсинг строк с юникодом и дополнительными пробелами."""
    content = (
        "2025-04-27 21:00:00,000 INFO django.request:"
        " Запрос с юникодом /api/v1/юзер/ 200 OK [192.168.1.105]\n"
        "2025-04-27 21:01:00,000 INFO django.request:"
        "    GET    /api/v1/spaces/    200 OK [192.168.1.106]\n"
    )
    log_file = create_log_file1(content)
    records = parse_log_file(log_file)
    assert records == [
        {"handler": "/api/v1/юзер/", "level": "INFO"},
        {"handler": "/api/v1/spaces/", "level": "INFO"},
    ]


def test_parse_log_only_django_request(create_log_file1):
    """Парсинг только строк с модулем django.request."""
    content = (
        "2025-03-28 12:01:42,000 WARNING django.security:"
        " IntegrityError: duplicate key value violates unique constraint\n"
        "2025-03-28 12:09:16,000 INFO django.request:"
        " GET /api/v1/cart/ 204 OK [192.168.1.93]\n"
    )
    log_file = create_log_file1(content)
    records = parse_log_file(log_file)
    # Должен обработать только строку с django.request
    assert records == [
        {"handler": "/api/v1/cart/", "level": "INFO"},
    ]


def test_parse_log_file_no_handler(create_log_file1):
    """
    Обработка строк без указания handler.

    Результат должен быть пустым списком.
    """
    content = (
        "2025-03-26 12:00:06,000 INFO django.request:"
        " Some message without handler\n"
    )
    log_file = create_log_file1(content)
    records = parse_log_file(log_file)
    # Нет handler, поэтому список должен быть пустым
    assert not records


def test_parse_log_file_empty_lines(create_log_file1):
    """Игнорирование пустых строк в логах."""
    content = (
        "\n"
        "2025-03-28 12:09:16,000 INFO django.request:"
        " GET /api/v1/cart/ 204 OK [192.168.1.93]\n"
    )
    log_file = create_log_file1(content)
    records = parse_log_file(log_file)

    assert records == [{"handler": "/api/v1/cart/", "level": "INFO"}]


def test_parse_log_file_line_with_insufficient_parts(create_log_file1):
    """
    Строки с недостаточным количеством частей.

    Игнорируются без ошибок.
    """
    content = ("short line\n2025-03-28 12:09:16,000"
               " INFO django.request: GET /api/v1/cart/"
               " 204 OK [192.168.1.93]\n")
    log_file = create_log_file1(content)
    records = parse_log_file(log_file)
    # Должен обработать только корректную строку
    assert records == [{"handler": "/api/v1/cart/", "level": "INFO"}]


def test_parse_log_file_various_levels(create_log_file1):
    """Корректный парсинг строк с разными уровнями логирования."""
    content = (
        "2025-04-27 20:15:10,123 WARNING django.request:"
        " Deprecated API call detected at"
        " /api/v1/old-endpoint/ [192.168.1.100]\n"
        "2025-04-27 20:16:45,456 DEBUG django.request:"
        " Query parameters received: {'page': '2', 'sort': 'asc'}"
        " at /api/v1/products/ [192.168.1.101]\n"
        "2025-04-27 20:17:30,789 CRITICAL django.request:"
        " Database connection lost during processing request"
        " /api/v1/orders/ [192.168.1.102]\n"
        "2025-04-27 20:18:05,321 WARNING django.request:"
        " Slow response time detected for handler"
        " /api/v1/users/ [192.168.1.103]\n"
        "2025-04-27 20:19:50,654 DEBUG django.request:"
        " Cache miss for key 'user_123_profile'"
        " at /api/v1/profile/ [192.168.1.104]\n"
    )
    log_file = create_log_file1(content)
    records = parse_log_file(log_file)
    expected = [
        {"handler": "/api/v1/old-endpoint/", "level": "WARNING"},
        {"handler": "/api/v1/products/", "level": "DEBUG"},
        {"handler": "/api/v1/orders/", "level": "CRITICAL"},
        {"handler": "/api/v1/users/", "level": "WARNING"},
        {"handler": "/api/v1/profile/", "level": "DEBUG"},
    ]
    assert records == expected
