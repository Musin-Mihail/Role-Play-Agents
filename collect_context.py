import os

OUTPUT_FILE = "context_for_ai.txt"
CURRENT_SCRIPT_NAME = os.path.basename(__file__)
IGNORE_DIRS = {
    ".git",
    ".vs",
    ".idea",
    ".vscode",
    "__pycache__",
    "env",
    "venv",
    "bin",
    "obj",
    "packages",
    "TestResults",
    "CopilotIndices",
}
IGNORE_EXTENSIONS = {
    ".exe",
    ".dll",
    ".pdb",
    ".suo",
    ".user",
    ".pyd",
    ".cache",
    ".vsidx",
    ".lref",
    ".resources",
    ".pyc",
    ".db",
    ".sqlite",
    ".db-shm",
    ".db-wal",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".ico",
    ".mp3",
    ".mp4",
    ".zip",
    ".tar",
    ".gz",
    ".rar",
    ".nupkg",
}
IGNORE_FILES = {
    OUTPUT_FILE,
    CURRENT_SCRIPT_NAME,
    "collect_context.py",
    "log.txt",
    "chronology.txt",
    "review_changes.txt",
    "LICENSE.md",
    ".gitignore",
    "package-lock.json",
    "yarn.lock",
    "Master_Prompt_Phase1.md",
    "Migration_Log_Phase1.md",
    "Master_Prompt_Phase2.md",
    "Migration_Log_Phase2.md",
}


def is_binary(file_path):
    try:
        with open(file_path, "rb") as f:
            chunk = f.read(1024)
            return b"\0" in chunk
    except Exception:
        return True


def collect_files(start_path):
    print(f"Сбор контекста из: {start_path}")
    with open(OUTPUT_FILE, "w", encoding="utf-8") as outfile:
        outfile.write(f"# Project Context\n# Root: {os.path.abspath(start_path)}\n\n")
        file_count = 0
        for root, dirs, files in os.walk(start_path):
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
            for file in files:
                if file in IGNORE_FILES:
                    continue
                _, ext = os.path.splitext(file)
                if ext.lower() in IGNORE_EXTENSIONS:
                    continue
                file_path = os.path.join(root, file)
                if is_binary(file_path):
                    continue
                try:
                    rel_path = os.path.relpath(file_path, start_path)
                    with open(
                        file_path, "r", encoding="utf-8", errors="replace"
                    ) as infile:
                        content = infile.read()
                        outfile.write("=" * 50 + "\n")
                        outfile.write(f"FILE: {rel_path}\n")
                        outfile.write("=" * 50 + "\n")
                        outfile.write(content + "\n\n")
                        print(f"Добавлен: {rel_path}")
                        file_count += 1
                except Exception as e:
                    print(f"Ошибка чтения {file_path}: {e}")
    print(f"\nГотово! Обработано файлов: {file_count}")


if __name__ == "__main__":
    collect_files(os.getcwd())
