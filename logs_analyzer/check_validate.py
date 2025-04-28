"""Модуль для проверки существования файлов по списку путей."""

import sys
from pathlib import Path


def validate_files(paths: list[Path]) -> bool:
    """
    Проверяет, что все пути в списке указывают на существующие файлы.

    Если хотя бы один файл не найден, выводит сообщение об ошибке
    в stderr и возвращает False.

    :param paths: Список путей к файлам для проверки
    :return: True, если все файлы существуют, иначе False
    """
    all_exist = True
    for path in paths:
        if not path.is_file():
            print(f"Ошибка пути {path}. Файл не найден", file=sys.stderr)
            return False
    return all_exist
