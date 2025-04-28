"""
Модуль тестов для функции validate_files.

Проверяет корректную обработку файлов.
Файлы существуют, отсутствуют и пустые списки файлов.
Корректность вывода ошибок в stderr.
"""

from pathlib import Path

from logs_analyzer.check_validate import validate_files


def test_validate_files_all_exist(tmp_path: Path):
    """
    Проверяет, что validate_files возвращает True.

    Создаёт несколько файлов во временной директории.
    Проверяет результат.
    """
    # Создаём несколько файлов
    files = [tmp_path / f"file{i}.log" for i in range(3)]
    for f in files:
        f.write_text("test")
    # Проверяем, что функция возвращает True
    assert validate_files(files) is True


def test_validate_files_empty_list():
    """
    Проверяет, что validate_files возвращает True.

    Для пустого списка файлов.
    """
    assert validate_files([]) is True


def test_validate_files_one_missing(tmp_path: Path, capsys):
    """
    validate_files возвращает False и выводит ошибку.

    Создаёт один существующий файл и один отсутствующий.
    """
    existing_file = tmp_path / "exists.log"
    existing_file.write_text("test")
    missing_file = tmp_path / "missing.log"
    # Проверяем, что функция возвращает False и выводит ошибку в stderr
    result = validate_files([existing_file, missing_file])
    captured = capsys.readouterr()
    assert result is False
    assert f"Ошибка пути {missing_file}" in captured.err


def test_validate_files_first_missing(tmp_path: Path, capsys):
    """
    validate_files сразу возвращает False и выводит ошибку.

    Первый файл в списке отсутствует.
    """
    missing_file = tmp_path / "missing.log"
    existing_file = tmp_path / "exists.log"
    existing_file.write_text("test")
    result = validate_files([missing_file, existing_file])
    captured = capsys.readouterr()
    assert result is False
    assert f"Ошибка пути {missing_file}" in captured.err
