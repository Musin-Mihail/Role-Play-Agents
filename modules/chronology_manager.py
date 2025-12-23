import os

CHRONOLOGY_FILE = "chronology.txt"


def read_chronology():
    """Читает хронологию событий из файла."""
    if not os.path.exists(CHRONOLOGY_FILE):
        return ""
    with open(CHRONOLOGY_FILE, "r", encoding="utf-8") as f:
        return f.read()


def add_to_chronology(event):
    """Добавляет новое событие в файл хронологии."""
    with open(CHRONOLOGY_FILE, "a", encoding="utf-8") as f:
        f.write(event + "\n")


def overwrite_chronology(text):
    """Перезаписывает весь файл хронологии новым текстом."""
    with open(CHRONOLOGY_FILE, "w", encoding="utf-8") as f:
        f.write(text.strip() + "\n")
