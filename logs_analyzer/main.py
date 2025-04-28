"""Модуль main содержит точку входа для CLI-приложения анализа логов Django."""

import argparse
import sys
from pathlib import Path

from logs_analyzer.analyze import analyze_logs
from logs_analyzer.check_validate import validate_files
from logs_analyzer.reports import REPORTS_REGISTRY
from logs_analyzer.utils import get_report_class


def main() -> None:
    """
    Основная функция запуска CLI-приложения.

    Парсит аргументы командной строки, проверяет существование лог-файлов,
    получает класс отчёта, выполняет анализ логов и выводит отчёт.

    :return: None
    :raises SystemExit: При ошибках валидации файлов,
     выборе отчёта или анализе логов
    """
    parser = argparse.ArgumentParser(
        description="Анализ логов приложения Django"
    )
    parser.add_argument(
        "log_files",
        nargs="+",
        type=Path,
        help="Пути к лог-файлам"
    )
    parser.add_argument(
        "--report",
        required=True,
        choices=REPORTS_REGISTRY.keys(),
        help="Тип отчёта"
    )
    args = parser.parse_args()

    if not validate_files(paths=args.log_files):
        sys.exit(1)

    report_class = get_report_class(report_name=args.report)

    try:
        report = analyze_logs(
            log_files=args.log_files, report_class=report_class
        )
    except (ValueError, ConnectionError, RuntimeError, OSError) as er:
        print(f"Ошибка при анализе логов: {er}", file=sys.stderr)
        sys.exit(1)
    report.print_report()


if __name__ == "__main__":
    main()
