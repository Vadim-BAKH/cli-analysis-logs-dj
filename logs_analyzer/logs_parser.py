"""Модуль содержит функцию для парсинга лог-файлов Django."""

from pathlib import Path


def parse_log_file(path: Path) -> list[dict[str, str]]:
    """
    Парсит лог-файл и извлекает записи с модулем 'django.request'.

    Каждая запись представлена словарём с ключами:
    - 'handler': путь обработчика запроса (например, '/api/v1/users/')
    - 'level': уровень логирования (например, 'INFO', 'ERROR')

    :param path: Путь к лог-файлу
    :return: Список словарей с информацией об
     обработчиках и уровнях логов
    """
    records = []
    with path.open(mode="r", encoding="utf-8") as file:
        for line in file:
            if not line.strip():
                continue
            parts = line.strip().split()
            if len(parts) < 6:
                continue
            module = parts[3].rstrip(":")
            if module != "django.request":
                continue

            level = parts[2].upper()

            handler = None
            for part in parts[5:]:
                if part.startswith("/"):
                    handler = part
                    break
            if handler:
                records.append({"handler": handler, "level": level})
        return records
