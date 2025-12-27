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

### Этап 2: Data Layer Implementation

### Действия ИИ:

- Создан модуль `backend/app/models/`.
- Реализована Pydantic-модель `GameState` (и вложенные `Character`, `Scene`, `Clothing`, etc.) для строгой типизации файла `state.json`.
- Реализованы DTO модели `TurnRequest` и `TurnResponse` для будущего API интерфейса.
- Проведена валидация существующего `state.json` через новые модели — структура данных подтверждена.

### Предложенные изменения/артефакты:

- Файл: `backend/app/models/game_state.py`
- Файл: `backend/app/models/api_dtos.py`
- Файл: `backend/app/models/__init__.py`

### Предложение ИИ для следующего этапа:

- Следующим шагом (Этап 3) необходимо перенести **Core Services (Infrastructure)**.
- Нужно мигрировать утилиты `read_state`/`save_state` (из `state_manager.py`) в сервис, использующий новые Pydantic-модели.
- Также нужно адаптировать `TranslatorAgent` под внедрение зависимостей (Dependency Injection), чтобы избавиться от глобальной инициализации OpenAI клиента.

### Этап 3: Core Migration (Part 1 - Infrastructure)

### Действия ИИ:

- Создана директория `backend/app/services`.
- Реализован `backend/app/core/deps.py` для Dependency Injection (предоставление OpenAI клиента).
- Реализован `GameStateService` (`backend/app/services/state_service.py`) — сервис для Stateless-работы с `state.json` с использованием Pydantic-моделей. Заменяет старый `state_manager.py`.
- Реализован `TranslatorService` (`backend/app/services/translator_service.py`) — сервис перевода, отвязанный от глобальных переменных и использующий DI. Заменяет `TranslatorAgent`.
- Написан скрипт `test_step_3.py` для проверки инфраструктурного слоя.

### Предложенные изменения/артефакты:

- Файл: `backend/app/core/deps.py`
- Файл: `backend/app/services/state_service.py`
- Файл: `backend/app/services/translator_service.py`
- Файл: `backend/app/services/__init__.py`

### Предложение ИИ для следующего этапа:

- Следующим шагом (Этап 4) необходимо выполнить **Core Migration (Part 2 - Logic Agents)**. Нужно рефакторить "интеллектуальных" агентов (`ActionSelector`, `MotivationGenerator`, `ActionConsequence`, `StoryWriter`, `StoryVerifier`) в Stateless-сервисы. Они должны перестать использовать `print`/`log_func` и начать возвращать типизированные данные (или словари), принимая зависимости через конструктор.

### Этап 4: Core Migration (Part 2 - Logic Agents)

### Действия ИИ:

- Создан модуль `backend/app/core/utils.py` с функциями `deep_merge_dicts`, `get_scene_context`, `get_characters_snapshot`, которые были портированы из legacy `game_utils.py` и адаптированы под Pydantic `GameState`.
- Создан файл `backend/app/services/agent_services.py`, содержащий 6 Stateless-сервисов:
  - `WorldDescriptorService`
  - `ActionSelectorService`
  - `MotivationGeneratorService`
  - `ActionConsequenceService`
  - `StoryWriterService`
  - `StoryVerifierService`
- Логика агентов полностью очищена от `print`/`input` и глобального состояния. Теперь они принимают `GameState` (Pydantic модель) и возвращают типизированные данные.
- Обновлен `backend/app/core/deps.py` для регистрации провайдеров новых сервисов (Dependency Injection).

### Предложенные изменения/артефакты:

- Файл: `backend/app/core/utils.py`
- Файл: `backend/app/services/agent_services.py`
- Файл: `backend/app/core/deps.py`
- Тест: `test_step_4.py`

### Предложение ИИ для следующего этапа:

- Следующим шагом (Этап 5) необходимо реализовать **Game Engine Service**. Это будет оркестратор, который заменит цикл `while True` из старого `main.py`. Он будет принимать ввод пользователя, вызывать цепочку сервисов (Selector -> Motivation -> Consequence -> Writer -> Verifier) и сохранять результат, используя `GameStateService`.

### Этап 5: Game Engine Service Implementation

### Действия ИИ:

- Создан `backend/app/services/chronicle_service.py` для управления историей игры и генерации саммари (аналог `chronology_manager.py`).
- Создан `backend/app/services/game_engine_service.py` — основной оркестратор, реализующий логику игрового хода (User Input -> State Update -> AI Logic -> Save).
- Обновлен `backend/app/core/deps.py` для внедрения `GameEngineService` и `ChronicleService`.
- Написан интеграционный тест `test_step_5.py`, проверяющий полный цикл хода без запуска HTTP-сервера.

### Предложенные изменения/артефакты:

- Файл: `backend/app/services/chronicle_service.py`
- Файл: `backend/app/services/game_engine_service.py`
- Файл: `backend/app/core/deps.py`
- Файл: `backend/app/services/__init__.py`

### Предложение ИИ для следующего этапа:

- Следующим шагом (Этап 6) нужно реализовать **API Layer**.
- Создать роутер `backend/app/api/endpoints/game.py`.
- Реализовать эндпоинт `POST /game/turn`, который будет принимать `TurnRequest`, вызывать `GameEngineService` и возвращать `TurnResponse`.
- Подключить роутер к основному приложению в `main.py`.

### Этап 6: API Layer Implementation

### Действия ИИ:

- Создана структура директорий `backend/app/api/endpoints`.
- Реализован роутер `backend/app/api/endpoints/game.py` с эндпоинтом `POST /turn`.
  - Эндпоинт принимает `TurnRequest`, использует DI для получения `GameEngineService` и возвращает `TurnResponse`.
  - Реализована обработка ошибок (404, 500) и логирование.
- Создан агрегатор роутеров `backend/app/api/api.py`.
- Обновлен `backend/app/main.py`: подключен `api_router` с префиксом API из настроек.
- Написан интеграционный тест `test_step_6.py` с использованием `TestClient`, проверяющий работу всего пайплайна через HTTP-интерфейс.

### Предложенные изменения/артефакты:

- Файл: `backend/app/api/endpoints/game.py`
- Файл: `backend/app/api/api.py`
- Файл: `backend/app/main.py`
- Тест: `test_step_6.py`

### Предложение ИИ для следующего этапа:

- Основная миграция завершена. Следующим шагом (Этап 7: Cleanup) необходимо удалить старые файлы (`main.py` в корне, `agents/`, `modules/`, старые тесты) и консольный `Launcher`, чтобы оставить чистую архитектуру Backend API.
