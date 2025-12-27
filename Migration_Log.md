# Журнал миграции Role-Play Engine на FastAPI

Этот документ описывает хронологию переноса проекта с консольной архитектуры на REST API.

### Этап 0: Инициализация процесса миграции

Поставлена задача рефакторинга проекта. Исходные данные: консольное приложение на Python с использованием OpenAI. Целевая архитектура: FastAPI, Pydantic, Stateless-подход.

### Текущее состояние (Legacy):

- Проект работает через `main.py` с бесконечным циклом `while True`.
- Ввод/вывод осуществляется через `print`/`input`.
- Агенты хранятся в памяти во время работы скрипта.
- Логирование пишет одновременно в консоль и файл.

### Глобальный план миграции (Roadmap):

1.  **Setup Phase:** Создание структуры папок, виртуального окружения, базового приложения FastAPI, настройки конфигов (`Settings`).
2.  **Data Layer:** Создание Pydantic-моделей для `state.json` (чтение/запись) и моделей Request/Response (DTO).
3.  **Core Refactoring:**
    - Адаптация агентов для работы через Dependency Injection.
    - Перенос утилит (`game_utils`, `state_manager`) в сервисный слой.
    - Удаление `input`/`print` из логики агентов.
4.  **API Implementation:**
    - Реализация эндпоинта `/health`.
    - Реализация `/game/start` (инициализация сессии).
    - Реализация `/game/turn` (основной игровой цикл: User Input -> AI Response).
5.  **Cleanup:** Удаление старого `main.py` и `Launcher`, финальная проверка.

### Предложение ИИ для следующего этапа (Этап 1):

**Цель:** Подготовить фундамент приложения.

- **Создать структуру директорий:**
  - `backend/app/api/` (для роутеров)
  - `backend/app/core/` (для config.py и logging)
  - `backend/app/models/` (для Pydantic схем)
  - `backend/app/services/` (для бизнес-логики и агентов)
- **Создать `requirements.txt`** с `fastapi`, `uvicorn`, `pydantic-settings`, `openai`.
- **Создать `backend/app/core/config.py`** (Pydantic Settings).
- **Создать минимальный `backend/app/main.py`** с запуском сервера.
