import os
import shutil
import argparse
from datetime import datetime

# --- Конфигурация категорий файлов ---
# Словарь, который сопоставляет расширения файлов с названиями папок.
# Добавляйте или изменяйте категории по своему усмотрению.
CATEGORIES = {
    # Изображения
    'jpg': 'Images', 'jpeg': 'Images', 'png': 'Images', 'gif': 'Images',
    'bmp': 'Images', 'tiff': 'Images', 'webp': 'Images', 'svg': 'Images',

    # Видео
    'mp4': 'Videos', 'mov': 'Videos', 'avi': 'Videos', 'mkv': 'Videos',
    'flv': 'Videos', 'wmv': 'Videos', 'webm': 'Videos',

    # Документы
    'pdf': 'Documents', 'doc': 'Documents', 'docx': 'Documents',
    'xls': 'Documents', 'xlsx': 'Documents', 'ppt': 'Documents',
    'pptx': 'Documents', 'txt': 'Documents', 'rtf': 'Documents',
    'odt': 'Documents', 'ods': 'Documents', 'odp': 'Documents',
    'csv': 'Documents', 'md': 'Documents',

    # Аудио
    'mp3': 'Audio', 'wav': 'Audio', 'flac': 'Audio', 'aac': 'Audio',
    'ogg': 'Audio', 'wma': 'Audio', 'm4a': 'Audio',

    # Архивы
    'zip': 'Archives', 'rar': 'Archives', '7z': 'Archives',
    'tar': 'Archives', 'gz': 'Archives', 'bz2': 'Archives', 'xz': 'Archives',

    # Исполняемые файлы / Установщики
    'exe': 'Executables', 'msi': 'Executables', 'dmg': 'Executables',
    'deb': 'Executables', 'rpm': 'Executables',

    # Код
    'py': 'Code', 'js': 'Code', 'html': 'Code', 'css': 'Code', 'json': 'Code',
    'xml': 'Code', 'c': 'Code', 'cpp': 'Code', 'java': 'Code', 'go': 'Code',
    'rb': 'Code', 'php': 'Code', 'sh': 'Code', 'bat': 'Code', 'yml': 'Code',
    'yaml': 'Code',

    # Таблицы и базы данных
    'sqlite': 'Databases', 'db': 'Databases',

    # Шрифты
    'ttf': 'Fonts', 'otf': 'Fonts', 'woff': 'Fonts', 'woff2': 'Fonts',
}

# --- Вспомогательные функции ---

def get_file_category(filename):
    """
    Определяет категорию файла по его расширению.
    Возвращает имя папки или 'Other' для неизвестных расширений.
    """
    _, ext = os.path.splitext(filename)
    if ext:
        ext = ext[1:].lower()  # Убираем точку и приводим к нижнему регистру
        return CATEGORIES.get(ext, 'Other')
    return 'No_Extension'

def get_file_creation_date(filepath):
    """
    Возвращает дату создания файла в формате YYYY-MM-DD.
    """
    try:
        # Для Windows и Unix систем os.path.getctime может означать разное
        # os.path.getmtime - дата последнего изменения
        # os.path.getctime - дата создания (Windows) / дата последнего изменения метаданных (Unix)
        # Для кроссплатформенности часто используют getmtime для "последней активности"
        # Но для "создания" на Unix-подобных системах может потребоваться stat()
        timestamp = os.path.getctime(filepath) # Для Windows это будет создание
        # Для Linux/macOS можно использовать os.stat(filepath).st_birthtime если доступно
        # Но getctime обычно достаточно для "более-менее" создания, или используем getmtime
        return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')
    except Exception as e:
        print(f"Ошибка при получении даты создания файла {filepath}: {e}")
        return datetime.now().strftime('%Y-%m-%d') # Возвращаем текущую дату в случае ошибки

def sanitize_filename(filename):
    """
    Удаляет недопустимые символы из имени файла для предотвращения ошибок ОС.
    """
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename

# --- Основная логика органайзера ---

def organize_files(source_dir, dry_run=False, rename_with_date=False, verbose=True):
    """
    Организует файлы в указанной директории.
    source_dir: Путь к директории для организации.
    dry_run: Если True, только показывает, что будет сделано, без выполнения.
    rename_with_date: Если True, добавляет дату создания к имени файла.
    verbose: Если True, выводит подробные сообщения о действиях.
    """
    if not os.path.isdir(source_dir):
        print(f"Ошибка: Директория '{source_dir}' не найдена.")
        return

    if verbose:
        print(f"\n{'[СУХОЙ ПРОГОН]' if dry_run else '[ОРГАНИЗАЦИЯ]'} Директория: {source_dir}")
        print(f"Переименование с датой: {'Включено' if rename_with_date else 'Выключено'}")
        print("-" * 50)

    # Получаем список всех элементов в директории
    items = os.listdir(source_dir)

    for item in items:
        # Полный путь к текущему элементу
        source_path = os.path.join(source_dir, item)

        # Пропускаем директории и сам скрипт (если он в той же папке)
        if os.path.isdir(source_path):
            if verbose:
                print(f"Пропущена директория: {item}")
            continue
        if item == os.path.basename(__file__): # Пропускаем сам скрипт
             if verbose:
                 print(f"Пропущен скрипт: {item}")
             continue


        # Определяем категорию файла
        category = get_file_category(item)
        target_category_dir = os.path.join(source_dir, category)

        # Создаем папку категории, если её нет
        if not os.path.exists(target_category_dir):
            if dry_run:
                if verbose:
                    print(f"[Сухой прогон] Будет создана папка: {target_category_dir}")
            else:
                try:
                    os.makedirs(target_category_dir)
                    if verbose:
                        print(f"Создана папка: {target_category_dir}")
                except OSError as e:
                    print(f"Ошибка при создании папки {target_category_dir}: {e}")
                    continue # Пропускаем файл, если не удалось создать папку

        # Формируем новое имя файла, если включено переименование с датой
        new_filename = item
        if rename_with_date:
            file_creation_date = get_file_creation_date(source_path)
            name_part, ext_part = os.path.splitext(item)
            new_filename = f"{name_part}_{file_creation_date}{ext_part}"
            new_filename = sanitize_filename(new_filename) # Очищаем имя файла

        # Определяем конечный путь для файла
        target_path = os.path.join(target_category_dir, new_filename)

        # Обработка конфликтов имен
        counter = 1
        original_target_path = target_path
        while os.path.exists(target_path) and os.path.isfile(target_path) and not os.path.samefile(source_path, target_path):
            name_part, ext_part = os.path.splitext(new_filename)
            target_path = os.path.join(target_category_dir, f"{name_part}_copy{counter}{ext_part}")
            counter += 1
            if counter > 1000: # Защита от бесконечного цикла, если что-то пошло не так
                print(f"Ошибка: Слишком много конфликтов для файла {item}. Пропуск.")
                break

        # Если файл уже существует в целевой папке и это тот же самый файл (т.е. он уже отсортирован)
        if os.path.exists(target_path) and os.path.isfile(target_path) and os.path.samefile(source_path, target_path):
            if verbose:
                print(f"Файл '{item}' уже находится в '{category}'. Пропущено.")
            continue


        # Выполнение перемещения или вывод информации в режиме сухого прогона
        if dry_run:
            if verbose:
                action = f"Будет перемещен: '{item}' -> '{target_path}'"
                if rename_with_date and new_filename != item:
                    action += f" (переименован в '{new_filename}')"
                print(f"[Сухой прогон] {action}")
        else:
            try:
                shutil.move(source_path, target_path)
                if verbose:
                    action = f"Перемещен: '{item}' -> '{target_path}'"
                    if rename_with_date and new_filename != item:
                        action += f" (переименован в '{new_filename}')"
                    print(action)
            except shutil.Error as e:
                print(f"Ошибка при перемещении файла '{item}' в '{target_path}': {e}")
            except Exception as e:
                print(f"Неизвестная ошибка с файлом '{item}': {e}")

    if verbose:
        print("-" * 50)
        print("Организация завершена!")

# --- Парсер аргументов командной строки ---

def main():
    parser = argparse.ArgumentParser(
        description="Консольный органайзер файлов: сортирует файлы по типам в подпапки."
    )
    parser.add_argument(
        '--path',
        type=str,
        default='.', # По умолчанию - текущая директория
        help='Путь к директории, которую нужно организовать. По умолчанию - текущая.'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Режим сухого прогона: показать, что будет сделано, без выполнения действий.'
    )
    parser.add_argument(
        '--rename-date',
        action='store_true',
        help='Добавлять дату создания файла к имени при переименовании.'
    )
    parser.add_argument(
        '--silent',
        action='store_true',
        help='Отключить подробный вывод сообщений о каждом действии.'
    )

    args = parser.parse_args()

    organize_files(
        source_dir=args.path,
        dry_run=args.dry_run,
        rename_with_date=args.rename_date,
        verbose=not args.silent
    )

if __name__ == '__main__':
    main()
