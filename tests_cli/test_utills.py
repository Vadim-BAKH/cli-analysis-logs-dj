"""
Модуль тестов для функции get_report_class из модуля utils.

Проверяет корректность обработки некорректных имён отчётов.
"""

import pytest
from logs_analyzer.utils import get_report_class


def test_get_report_class_invalid():
    """
    Проверяет несуществующий отчёт.

    При запросе несуществующего отчёта выбрасывается ValueError.
    """
    with pytest.raises(ValueError) as exc_info:
        get_report_class("nonexistent_report")
    assert "Отчёт 'nonexistent_report' не найден." in str(exc_info.value)
