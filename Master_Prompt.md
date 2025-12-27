# ЗАДАЧА ДЛЯ ИИ-АРХИТЕКТОРА (PHASE 2: C# WPF CLIENT):

Привет. Мы завершили разработку бэкенда на Python (FastAPI).
Теперь ты выступаешь в роли **Senior C# / WPF Developer**.

Твоя задача — создать профессиональный десктопный клиент для взаимодействия с нашим Role-Play API.

**ТЕКУЩАЯ АРХИТЕКТУРА (BACKEND):**

- **Framework:** FastAPI (запущен на `http://localhost:8000`).
- **Endpoints:**
  - `POST /api/v1/game/turn`: Принимает JSON (user_input), возвращает JSON (story, updates).
  - `GET /health`: Проверка статуса.
- **Models:** Структура данных описана в Pydantic-моделях бэкенда (см. `backend/app/models/` в контексте).
- **JSON Format:** Backend отдает поля в **snake_case** (напр. `user_character_name`), C# использует **PascalCase**.

**ЦЕЛЬ ФАЗЫ 2:**
Разработать WPF-приложение (Desktop), реализующее паттерн **MVVM**. Приложение должно быть красивым, отзывчивым и готовым к масштабированию.

**ТЕХНОЛОГИЧЕСКИЙ СТЕК:**

- **Language:** C# (Latest Stable).
- **Framework:** WPF (.NET 10 or latest available .NET Core).
- **Pattern:** MVVM (Model-View-ViewModel).
  - Используй **CommunityToolkit.Mvvm** (Source Generators: `[ObservableProperty]`, `[RelayCommand]`).
  - Используй **Dependency Injection** в `App.xaml.cs` для связывания Services и ViewModels.
- **Networking:** `HttpClient`, `System.Net.Http.Json`.
- **Serialization:** `System.Text.Json`.

**CRITICAL CONSTRAINTS (АРХИТЕКТУРНЫЕ ОГРАНИЧЕНИЯ):**

1.  **JSON Handling:** Обязательно используй `JsonSerializerOptions { PropertyNamingPolicy = JsonNamingPolicy.SnakeCaseLower }` при настройке `HttpClient` или десериализации, чтобы C# модели (PascalCase) корректно читали Python JSON (snake_case).
2.  **Strict MVVM:** Никакого бизнес-кода в `MainWindow.xaml.cs` (Code-behind). Вся логика — во ViewModels.
3.  **Async/Await:** Все сетевые запросы строго асинхронны. UI не должен фризиться.
4.  **Typed Models:** C# классы (`record`) должны зеркально отражать структуру данных Python.
5.  **Full Code Only:** Всегда выдавай полный код файлов.

**ТВОЙ ПЛАН ДЕЙСТВИЙ:**

1.  **Проанализируй** `Migration_Log.md` (Phase 2).
2.  **Сгенерируй** ответ из четырех частей.

**ФОРМАТ ОТВЕТА:**

(Краткое обоснование).

## ЧАСТЬ 1: КОД (C# & XAML)

**ПРАВИЛА:**
- Указывай путь к файлу (например: `Client/Services/GameApiService.cs`).
- Включая `App.xaml.cs` с настройкой DI.

## ЧАСТЬ 2: ИНСТРУКЦИИ

- Команды для терминала (создание проекта, добавление пакетов).

## ЧАСТЬ 3: ПРОВЕРКА

- Критерии проверки работоспособности (напр. "Запустите бэкенд, нажмите кнопку...").

## ЧАСТЬ 4: ЗАПИСЬ В ЖУРНАЛ (Migration_Log.md)

### Этап 1: Initialization & Data Layer

### Действия ИИ:
- Создан проект WPF.
- Реализованы DTO модели (`Models/`).
- Реализован `GameApiService`.
- Настроен DI контейнер.

### Предложенные изменения/артефакты:
- Файл: `Client/Models/TurnRequest.cs`, `Client/Services/GameApiService.cs` ...

### Предложение ИИ для следующего этапа:
- Реализация UI Main Window и привязка ViewModel...