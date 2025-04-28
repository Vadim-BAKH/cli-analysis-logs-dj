"""Модуль содержит класс HandlerReport."""

from collections import defaultdict

LOG_LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


class HandlerReport:
    """
    Класс для формирования отчёта.

    Сохраняет количество запросов по уровням логирования.
    Сохраняет общее количество запросов.
    """

    def __init__(self) -> None:
        """
        Инициализирует структуру данных.

        Данные для хранения статистики.
        Счётчик общего количества запросов.
        """
        self.data: dict[str, dict[str, int]] =\
            defaultdict(lambda: defaultdict(int))
        self.total_requests = 0

    def add_data(self, records: list[dict[str, str]]) -> None:
        """
        Добавляет данные из списка записей логов в отчёт.

        Каждая запись должна содержать ключи 'handler' и 'level'.
        Увеличивает счётчики по уровням логирования для соответствующего
        обработчика и обновляет общее количество запросов.

        :param records: Список словарей с данными логов,
                        где каждый словарь содержит:
                        - 'handler': путь обработчика запроса (str)
                        - 'level': уровень логирования (str)
        :return: None
        """
        for record in records:
            handler = record["handler"]
            level = record["level"]
            if level not in LOG_LEVELS:
                continue
            self.data[handler][level] += 1
            self.total_requests += 1

    def print_report(self) -> None:
        """
        Выводит отчёт по обработчикам запросов в табличном виде.

        Отчёт содержит общее количество запросов и распределение
        по уровням логирования для каждого обработчика, а также
        итоги по всем обработчикам.

        :return: None
        """
        print(f"\nTotal requests: {self.total_requests}\n")
        header = ["HANDLER"] + LOG_LEVELS
        handler_width = 20
        level_width = 10
        header_str = header[0].ljust(handler_width) + "".join(
            h.ljust(level_width) for h in header[1:]
        )
        print(header_str)

        for handler in sorted(self.data.keys()):

            counts = [
                str(self.data[handler].get(level, 0)).ljust(level_width)
                for level in LOG_LEVELS
            ]
            print(f"{handler.ljust(handler_width)}{''.join(counts)}")

        totals = [
            str(sum(self.data[h].get(level, 0) for h in self.data))
            .ljust(level_width)
            for level in LOG_LEVELS
        ]
        print(f"{''.ljust(handler_width)}{''.join(totals)}")
