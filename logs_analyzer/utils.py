"""Модуль utils содержит вспомогательные функции для работы с отчетами."""

from logs_analyzer.reports import REPORTS_REGISTRY


def get_report_class(report_name: str) -> type:
    """
    Получить класс отчёта по его имени из реестра REPORTS_REGISTRY.

    :param report_name: Имя отчёта (ключ в REPORTS_REGISTRY)
    :return: Класс отчёта, соответствующий имени
    :raises ValueError: Если отчёт с таким именем не найден в реестре
    """
    report_class = REPORTS_REGISTRY.get(report_name)
    if not report_class:
        raise ValueError(f"Отчёт '{report_name}' не найден.")
    return report_class
