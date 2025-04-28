"""
Модуль тестов для основного запуска приложения.

Содержит тесты для проверки аргументов командной строки.
Тесты обработки ошибок и успешного выполнения анализа логов.
"""

import runpy
import sys
from pathlib import Path
from unittest import mock

import pytest
from logs_analyzer import main as log_analyzer_main


@pytest.fixture
def valid_log_files(tmp_path: Path) -> list[Path]:
    """
    Фикстура для создания списка лог-файлов с тестовым содержимым.

    :param tmp_path: Временная директория pytest
    :return: Список путей к созданным лог-файлам
    """
    files = []
    content = "2025-03-26 12:00:06,000 INFO django.request /api/v1/users/\n"
    for i in range(2):
        file = tmp_path / f"log{i}.log"
        file.write_text(content)
        files.append(file)
    return files


def test_help_shows_description(monkeypatch, capsys):
    """
    --help выводится описание программы и происходит выход с кодом 0.

    :param monkeypatch: фикстура для изменения argv
    :param capsys: фикстура для захвата вывода
    """
    testargs = ["prog", "--help"]
    monkeypatch.setattr(sys, "argv", testargs)
    with pytest.raises(SystemExit) as e:
        log_analyzer_main.main()
    captured = capsys.readouterr()
    assert "Анализ логов" in captured.out
    assert e.value.code == 0


def test_missing_required_report(monkeypatch, valid_log_files, capsys):
    """
    При отсутствии --report программа завершается с ошибкой.

    :param monkeypatch: фикстура для изменения argv
    :param valid_log_files: фикстура с валидными лог-файлами
    :param capsys: фикстура для захвата вывода
    """
    testargs = ["prog"] + [str(f) for f in valid_log_files]
    monkeypatch.setattr(sys, "argv", testargs)
    with pytest.raises(SystemExit) as e:
        log_analyzer_main.main()
    captured = capsys.readouterr()
    assert "error" in captured.err.lower() or "usage" in captured.out.lower()
    assert e.value.code != 0


def test_invalid_report_value(monkeypatch, valid_log_files, capsys):
    """
    Передача недопустимого значения --report.

    Программа завершается с ошибкой.

    :param monkeypatch: фикстура для изменения argv
    :param valid_log_files: фикстура с валидными лог-файлами
    :param capsys: фикстура для захвата вывода
    """
    testargs = (
        ["prog"]
        + [str(f) for f in valid_log_files]
        + ["--report", "invalid_report"]
    )
    monkeypatch.setattr(sys, "argv", testargs)
    with pytest.raises(SystemExit) as e:
        log_analyzer_main.main()
    captured = capsys.readouterr()
    # Проверяем, что в stderr или stdout есть сообщение об ошибке выбора
    assert ("invalid choice" in captured.err
            or "invalid choice"
            in captured.out)
    assert e.value.code != 0


def test_validate_files_failure(monkeypatch, valid_log_files):
    """
    При провале валидации файлов программа завершается с кодом 1.

    :param monkeypatch: фикстура для изменения argv
    :param valid_log_files: фикстура с валидными лог-файлами
    """
    monkeypatch.setattr(
        sys,
        "argv",
        ["prog"]
        + [str(f) for f in valid_log_files]
        + ["--report", "handlers"],
    )
    with mock.patch("logs_analyzer.main.validate_files", return_value=False):
        with pytest.raises(SystemExit) as e:
            log_analyzer_main.main()
        assert e.value.code == 1


def test_successful_run(monkeypatch, valid_log_files) -> None:
    """
    Тестирует успешный запуск main() с мокированием analyze_logs.

    Устанавливает аргументы командной строки.
    Использует DummyReport с методом display_report для заглушки.
    Проверяет, что analyze_logs вызывается ровно один раз.
    """
    monkeypatch.setattr(
        sys,
        "argv",
        ["prog"]
        + [str(f) for f in valid_log_files]
        + ["--report", "handlers"],
    )

    class DummyReport: # pylint: disable=too-few-public-methods
        """
        Заглушка класса отчёта для тестирования.

        Метод display_report имитирует вывод отчёта.
        """

        def print_report(self) -> None:
            """
            Выводит сообщение о печати отчёта.

            Используется для проверки вызова метода в тестах.
            """
            print("Report printed")

    with mock.patch(
        "logs_analyzer.main.analyze_logs", return_value=DummyReport()
    ) as mock_analyze:
        log_analyzer_main.main()
        mock_analyze.assert_called_once()


def test_exit_on_analyze_exception(monkeypatch, valid_log_files):
    """
    Возникновение исключения в analyze_logs.

    Программа корректно завершает работу с кодом 1.

    :param monkeypatch: фикстура для изменения argv
    :param valid_log_files: фикстура с валидными лог-файлами
    """
    monkeypatch.setattr(
        sys,
        "argv",
        ["prog"]
        + [str(f) for f in valid_log_files]
        + ["--report", "handlers"],
    )

    def raise_error(*args, **kwargs):
        """
        Выводит переданные аргументы в stderr и возбуждает RuntimeError.

        :param args: Позиционные аргументы
        :param kwargs: Именованные аргументы
        :raises RuntimeError: всегда возбуждается после вывода аргументов
        """
        print("Received args:", args, file=sys.stderr)
        print("Received kwargs:", kwargs, file=sys.stderr)
        raise RuntimeError("Test error")

    with mock.patch(
            "logs_analyzer.main.analyze_logs",
            side_effect=raise_error
    ):
        with pytest.raises(SystemExit) as e:
            log_analyzer_main.main()
        assert e.value.code == 1


@pytest.mark.parametrize(
    "exc", [ValueError("val"), ConnectionError("conn"), OSError("os")]
)
def test_exit_on_various_exceptions(monkeypatch, valid_log_files, exc) -> None:
    """
    Возникновение различных исключений в analyze_logs.

    Программа корректно завершает работу с кодом 1.

    :param monkeypatch: фикстура для изменения argv
    :param valid_log_files: фикстура с валидными лог-файлами
    :param exc: Исключение для тестирования
    """
    monkeypatch.setattr(
        sys,
        "argv",
        ["prog"]
        + [str(f) for f in valid_log_files]
        + ["--report", "handlers"],
    )

    with mock.patch("logs_analyzer.main.analyze_logs", side_effect=exc):
        with pytest.raises(SystemExit) as e:
            log_analyzer_main.main()
        assert e.value.code == 1


def test_main_exit_on_invalid_report(monkeypatch, valid_log_files):
    """
    Передача некорректного имени отчёта.

    Программа завершается с кодом 2.

    :param monkeypatch: фикстура для изменения argv
    :param valid_log_files: фикстура с валидными лог-файлами
    """
    monkeypatch.setattr(
        sys,
        "argv",
        ["prog"]
        + [str(f) for f in valid_log_files]
        + ["--report", "invalid_report"],
    )

    with mock.patch(
        "logs_analyzer.utils.get_report_class",
        side_effect=ValueError("Отчёт 'invalid_report' не найден."),
    ):
        with pytest.raises(SystemExit) as e:
            log_analyzer_main.main()
        assert e.value.code == 2


def test_main_entry_point(monkeypatch, valid_log_files) -> None:
    """
    Запуск logs_analyzer.main как скрипта через runpy.

    :param monkeypatch: фикстура для изменения argv
    :param valid_log_files: фикстура с валидными лог-файлами
    """
    monkeypatch.setattr(
        sys,
        "argv",
        ["prog"]
        + [str(f) for f in valid_log_files]
        + ["--report", "handlers"],
    )
    sys.modules.pop("logs_analyzer.main", None)  # Удаляем из кэша импортов
    runpy.run_module("logs_analyzer.main", run_name="__main__")
