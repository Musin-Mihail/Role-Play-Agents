# Журнал миграции Role-Play Engine на FastAPI

Этот документ описывает хронологию переноса проекта с консольной архитектуры на REST API.

### Этап 0: Инициализация процесса миграции

Поставлена задача рефакторинга проекта. Исходные данные: консольное приложение на Python с использованием OpenAI. Целевая архитектура: FastAPI, Pydantic, Stateless-подход.

### Текущее состояние (Legacy):

- Проект работает через `main.py` с бесконечным циклом `while True`.
- Ввод/вывод осуществляется через `print`/`input`.
- Агенты хранятся в памяти во время работы скрипта.
- Хардкод путей и API URL.

### Глобальный план миграции (Roadmap):

1.  **Setup Phase:** Создание структуры папок, `requirements.txt`, настройка `config.py` (Pydantic Settings) и базового `main.py`.
2.  **Data Layer:** Создание Pydantic-моделей для `state.json` (Game State) и DTO моделей для Request/Response.
3.  **Core Migration (Part 1 - Infrastructure):**
    - Перенос утилит (`game_utils`, `state_manager`, `chronology_manager`) в сервисный слой (`backend/app/services`).
    - Адаптация простых агентов (`TranslatorAgent`, `WorldDescriptorAgent`) под Dependency Injection.
4.  **Core Migration (Part 2 - Logic Agents):**
    - Рефакторинг сложных агентов (`ActionSelector`, `StoryWriter`, `MotivationGenerator`) — удаление `print`, переход на возвращение Pydantic объектов или словарей.
5.  **Game Engine Service:**
    - Создание сервиса-оркестратора (`GameEngine`), который заменяет логику цикла из старого `main.py`. Он должен принимать состояние и ввод, и возвращать результат хода (Stateless).
6.  **API Implementation:**
    - Реализация роутеров FastAPI (`/api/v1/game/turn`, `/api/v1/game/start`). Подключение `GameEngine`.
7.  **Cleanup:** Удаление старого `main.py`, `Launcher` и временных файлов.

---

### Предложение ИИ для следующего этапа (Этап 1):

**Цель:** Подготовить фундамент приложения.

- **Создать структуру директорий:**
  - `backend/app/api/` (роутеры)
  - `backend/app/core/` (конфигурация, логгирование)
  - `backend/app/models/` (схемы данных)
  - `backend/app/services/` (бизнес-логика)
- **Создать `requirements.txt`** (fastapi, uvicorn, pydantic-settings, openai).
- **Создать `backend/app/core/config.py`**:
  - Реализовать класс `Settings` с загрузкой `OPENAI_API_KEY`, `API_BASE_URL` из `.env`.
- **Создать `backend/app/main.py`**:

  - Базовая инициализация FastAPI app.
  - Настройка CORS middleware.
  - Health check endpoint.

### Этап 1: Setup Phase

### Действия ИИ:

- Создана базовая структура директорий `backend/app/`.
- Сформирован `requirements.txt` с основными зависимостями (FastAPI, Uvicorn, Pydantic).
- Реализована конфигурация через `pydantic-settings` (`backend/app/core/config.py`).
- Создан базовый файл приложения `backend/app/main.py` с Health Check эндпоинтом и CORS.

### Предложенные изменения/артефакты:

- Файл: `backend/requirements.txt`
- Файл: `backend/app/core/config.py`
- Файл: `backend/app/main.py`

### Предложение ИИ для следующего этапа:

- Следующим шагом логично будет реализовать **Data Layer**: создать Pydantic-модели, отражающие структуру `state.json` и DTO для взаимодействия с API. Это необходимо перед переносом логики сервисов.
