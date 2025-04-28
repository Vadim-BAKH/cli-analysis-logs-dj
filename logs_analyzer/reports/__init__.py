"""
Пакет reports содержит реализации различных типов отчётов для анализа логов.

REPORTS_REGISTRY - реестр доступных классов отчётов.
"""

from logs_analyzer.reports.handlers import HandlerReport

REPORTS_REGISTRY: dict[str, type] = {
    "handlers": HandlerReport,
}
