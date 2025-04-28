"""
Модуль тестов для функции analyze_logs.

Использует класс отчёта HandlerReport.
Проверяет корректность анализа лог-файлов.
Обрабатывает.
Одиночные и множественные файлы.
Пустые списки и взаимодействие с моками.
"""

from pathlib import Path
from unittest.mock import MagicMock

import pytest
from logs_analyzer.analyze import analyze_logs
from logs_analyzer.reports.handlers import HandlerReport


@pytest.fixture
def create_log_file(tmp_path: Path) -> callable:
    """
    Фикстура для создания временного лог-файла содержимым.

    :param tmp_path: временная директория pytest
    :return: функция, принимающая содержимое и
             необязательное имя файла, возвращающая путь к файлу
    """

    def _create(content: str, filename: str = "test.log") -> Path:
        """
        Создаёт временный файл с заданным содержимым и возвращает путь к нему.

        :param content: Текстовое содержимое файла
        :param filename: Имя файла (по умолчанию "test.log")
        :return: Путь к созданному файлу
        """
        file = tmp_path / filename
        file.write_text(content, encoding="utf-8")
        return file

    return _create


def test_analyze_logs_single_file(create_log_file):
    """
    Проверяет корректный анализ одного лог-файла.

    Правильное количество запросов.
    Данные по обработчику.
    """
    content = ("2025-04-27 20:15:10,123 INFO django.request:"
               " GET /api/v1/test/ 200 OK [192.168.1.1]\n")
    log_file = create_log_file(content)

    report = analyze_logs([log_file], HandlerReport)

    # Проверяем, что отчёт содержит правильные данные
    assert report.total_requests == 1
    assert "/api/v1/test/" in report.data
    assert report.data["/api/v1/test/"]["INFO"] == 1


def test_analyze_logs_multiple_files(create_log_file):
    """
    Проверяет анализ нескольких лог-файлов.

    Отчёт аккумулирует данные по всем файлам корректно.
    """
    content1 = ("2025-04-27 20:15:10,123 INFO django.request:"
                " GET /api/v1/test1/ 200 OK [192.168.1.1]\n")
    content2 = ("2025-04-27 20:16:10,456 ERROR django.request:"
                " GET /api/v1/test2/ 500 Internal"
                " Server Error [192.168.1.2]\n")

    log_file1 = create_log_file(content1, filename="test1.log")
    log_file2 = create_log_file(content2, filename="test2.log")

    report = analyze_logs([log_file1, log_file2], HandlerReport)

    assert report.total_requests == 2
    assert "/api/v1/test1/" in report.data
    assert "/api/v1/test2/" in report.data
    assert report.data["/api/v1/test1/"]["INFO"] == 1
    assert report.data["/api/v1/test2/"]["ERROR"] == 1


def test_analyze_logs_empty_list():
    """
    Проверяет анализ пустого списка файлов.

    Возвращает пустой отчёт.
    """
    report = analyze_logs([], HandlerReport)
    assert report.total_requests == 0
    assert len(report.data) == 0


def test_analyze_logs_with_mock(monkeypatch):
    """
    Проверяет взаимодействие analyze_logs.

    Взаимодействие функцией parse_log_file.
    С методом add_data класса отчёта.
    Использует моки для проверки вызовов и передачи данных.
    """
    mock_parse = MagicMock(
        return_value=[{"handler": "/mock/", "level": "INFO"}]
    )
    monkeypatch.setattr(
        "logs_analyzer.analyze.parse_log_file", mock_parse
    )

    mock_report_class = MagicMock()
    mock_report_instance = mock_report_class.return_value

    log_files = [Path("file1.log"), Path("file2.log")]

    analyze_logs(log_files, mock_report_class)

    # Проверяем, что parse_log_file вызвался для каждого файла
    assert mock_parse.call_count == 2

    # Проверяем, что add_data вызвался с результатами парсера
    assert mock_report_instance.add_data.call_count == 2
    mock_report_instance.add_data.assert_any_call(
        [{"handler": "/mock/", "level": "INFO"}]
    )
