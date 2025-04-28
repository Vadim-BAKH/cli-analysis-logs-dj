"""Модуль многопоточного анализа лог-файлов и генерации отчёта."""

from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

from logs_analyzer.logs_parser import parse_log_file


def analyze_logs(log_files: list[Path], report_class: type) -> Any:
    """
    Анализирует лог-файлы и формирует отчёт.

    Анализирует в многопоточном режиме параллельно.
    Формирует отчёт указанного типа.

    :param log_files: Список путей к анализируемым лог-файлам
    :param report_class: Класс отчёта, должен реализовывать методы:
                        - add_data() для добавления данных
                        - print_report() для вывода результата
    :return: Экземпляр сформированного отчёта
    """
    report = report_class()
    with ThreadPoolExecutor() as tpe:
        futures = [
            tpe.submit(parse_log_file, log_file) for log_file in log_files
        ]
        for future in as_completed(futures):
            record = future.result()
            report.add_data(record)
    return report
