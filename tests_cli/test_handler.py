"""
Модуль тестов для класса HandlerReport.

Из модуля logs_analyzer.reports.handlers.
Корректность подсчёта и накопления данных.
Игнорирование некорректных уровней.
Правильность вывода отчёта.
"""

from logs_analyzer.reports.handlers import LOG_LEVELS, HandlerReport


def test_initial_state() -> None:
    """
    Проверяет начальное состояние экземпляра HandlerReport.

    Убеждается, что total_requests равен 0.
    data является словарём и изначально пуст.
    """
    report = HandlerReport()
    assert report.total_requests == 0
    assert isinstance(report.data, dict)
    assert len(report.data) == 0


def test_add_data_counts_correctly():
    """
    Проверяет корректность.

    Добавление и подсчёт данных по уровням и обработчикам.
    """
    report = HandlerReport()
    records = [
        {"handler": "/api/v1/users/", "level": "INFO"},
        {"handler": "/api/v1/users/", "level": "ERROR"},
        {"handler": "/api/v1/orders/", "level": "INFO"},
        {"handler": "/api/v1/users/", "level": "INFO"},
    ]
    report.add_data(records)
    assert report.total_requests == 4
    assert report.data["/api/v1/users/"]["INFO"] == 2
    assert report.data["/api/v1/users/"]["ERROR"] == 1
    assert report.data["/api/v1/orders/"]["INFO"] == 1


def test_add_data_ignores_invalid_levels():
    """
    Записи с некорректными уровнями логирования.

    Записи игнорируются.
    """
    report = HandlerReport()
    records = [
        {"handler": "/api/v1/users/", "level": "INFO"},
        {"handler": "/api/v1/users/", "level": "INVALID"},
        {"handler": "/api/v1/orders/", "level": "ERROR"},
        {"handler": "/api/v1/orders/", "level": "UNKNOWN"},
    ]
    report.add_data(records)
    assert report.total_requests == 2
    assert report.data["/api/v1/users/"]["INFO"] == 1
    assert report.data["/api/v1/orders/"]["ERROR"] == 1
    assert "INVALID" not in report.data["/api/v1/users/"]
    assert "UNKNOWN" not in report.data["/api/v1/orders/"]


def test_add_data_empty_list() -> None:
    """
    Поведение при добавлении пустого списка записей.

    Пропускает без ошибки.
    """
    report = HandlerReport()
    report.add_data([])
    assert report.total_requests == 0
    assert len(report.data) == 0


def test_print_report_output(capsys):
    """
    Метод print_report корректно выводит отчёт.

    Проверяет выводы.
    """
    report = HandlerReport()
    records = [
        {"handler": "/api/v1/users/", "level": "INFO"},
        {"handler": "/api/v1/users/", "level": "ERROR"},
        {"handler": "/api/v1/orders/", "level": "INFO"},
    ]
    report.add_data(records)
    report.print_report()

    captured = capsys.readouterr()
    output = captured.out

    # Проверяем, что в выводе есть заголовок
    assert "Total requests: 3" in output
    for level in LOG_LEVELS:
        assert level in output

    # Проверяем, что обработчики присутствуют в выводе
    assert "/api/v1/users/" in output
    assert "/api/v1/orders/" in output

    # Проверяем, что количество для INFO и ERROR корректно отображается
    assert "2" in output  # INFO для /api/v1/users/
    assert "1" in output  # ERROR для /api/v1/users/ и INFO для /api/v1/orders/


def test_report_accumulates_data():
    """
    Проверяет накопление данных.

    Последовательные вызовы add_data.
    """
    report = HandlerReport()
    records1 = [
        {"handler": "/api/v1/users/", "level": "INFO"},
        {"handler": "/api/v1/orders/", "level": "ERROR"},
    ]
    records2 = [
        {"handler": "/api/v1/users/", "level": "WARNING"},
        {"handler": "/api/v1/orders/", "level": "ERROR"},
    ]
    report.add_data(records1)
    report.add_data(records2)

    assert report.total_requests == 4
    assert report.data["/api/v1/users/"]["INFO"] == 1
    assert report.data["/api/v1/users/"]["WARNING"] == 1
    assert report.data["/api/v1/orders/"]["ERROR"] == 2


def test_print_report_handlers_sorted_alphabetically(capsys):
    """
    Проверяет сортировку обработчиков в выводе отчёта.

    Отсортированы по алфавиту.
    """
    report = HandlerReport()
    records = [
        {"handler": "/api/v1/orders/", "level": "INFO"},
        {"handler": "/api/v1/users/", "level": "ERROR"},
        {"handler": "/api/v1/checkout/", "level": "WARNING"},
    ]
    report.add_data(records)
    report.print_report()

    captured = capsys.readouterr()
    output = captured.out

    # Извлечём строки с обработчиками (пропускаем заголовок и пустые строки)
    lines = [
        line
        for line in output.splitlines()
        if line
        and not line.startswith("Total requests")
        and not line.startswith("HANDLER")
    ]

    # Получим список обработчиков в порядке вывода
    handlers_in_output = [line.split()[0] for line in lines]

    # Проверяем, что список отсортирован по алфавиту
    assert handlers_in_output == sorted(handlers_in_output)
