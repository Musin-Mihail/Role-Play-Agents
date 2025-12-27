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
- **JSON Format:** Backend отдает поля в **snake_case** (напр. `user_character_name`), C# использует **PascalCase**. Вложенность JSON (Scene, Characters, Clothing) должна быть полностью соблюдена.

**ЦЕЛЬ ФАЗЫ 2:**
Разработать WPF-приложение (Desktop), реализующее паттерн **MVVM**. Приложение должно быть красивым, отзывчивым и готовым к масштабированию.

**ТЕХНОЛОГИЧЕСКИЙ СТЕК:**

- **Language:** C# (Latest Stable).
- **Framework:** WPF (.NET 9).
- **Pattern:** MVVM (Model-View-ViewModel).
  - Используй **CommunityToolkit.Mvvm** (Source Generators: `[ObservableProperty]`, `[RelayCommand]`).
  - Используй **Dependency Injection** (`Microsoft.Extensions.Hosting`) в `App.xaml.cs`.
  - **Configuration:** Используй `appsettings.json` для хранения `BaseUrl`.
- **Networking:** `HttpClient` (через `IHttpClientFactory`), `System.Net.Http.Json`.
- **Serialization:** `System.Text.Json`.

**CRITICAL CONSTRAINTS (АРХИТЕКТУРНЫЕ ОГРАНИЧЕНИЯ):**

1.  **JSON Handling & Interop:**
    - Обязательно используй `JsonSerializerOptions { PropertyNamingPolicy = JsonNamingPolicy.SnakeCaseLower }`.
    - Добавь `Converters.Add(new JsonStringEnumConverter())`, так как Python может отдавать enum как строки.
    - **Важно (Nullability):** Используй **Nullable Reference Types** (например, `string?`, `int?`). Поля, которые в Python моделях помечены как `Optional` или могут быть `None`, в C# DTO _обязательно_ должны быть nullable.
2.  **Data Structures:**
    - Для DTO моделей используй `public record class` (для иммутабельности).
    - Структура классов должна зеркально отражать вложенность Python моделей (включая `Clothing`, `InteractiveObject`, `Character`).
3.  **Strict MVVM:** Никакого бизнес-кода в `MainWindow.xaml.cs` (Code-behind). Вся логика — во ViewModels.
4.  **Async/Await:** Все сетевые запросы строго асинхронны. UI не должен фризиться. Реализуй базовую обработку `HttpRequestException`.
5.  **DI & Configuration:** `BaseUrl` должен читаться из `appsettings.json` и внедряться через `IOptions<AppConfig>` или конфигурироваться при регистрации `HttpClient`.
6.  **Full Code Only:** Всегда выдавай полный код файлов.

**ТВОЙ ПЛАН ДЕЙСТВИЙ:**

1.  **Проанализируй** `Migration_Log.md` (Phase 2).
2.  **Сгенерируй** ответ, сфокусированный на **Слое Данных (Models + Services)** и **Инфраструктуре**. Не пиши пока UI-код (XAML/ViewModels), это будет следующий шаг.

**ФОРМАТ ОТВЕТА:**

(Краткое обоснование).

## ЧАСТЬ 1: КОД (C# & JSON)

**ПРАВИЛА:**

- Указывай путь к файлу (например: `Client/Services/GameApiService.cs`).
- Включая `App.xaml.cs` с настройкой DI и `appsettings.json`.

## ЧАСТЬ 2: ИНСТРУКЦИИ

- Команды для терминала (создание проекта, добавление пакетов).
- Структура папок.

## ЧАСТЬ 3: ПРОВЕРКА

- Критерии проверки работоспособности (напр. "Запустите бэкенд, проверьте, что данные десериализуются без ошибок...").

## ЧАСТЬ 4: ЗАПИСЬ В ЖУРНАЛ (Migration_Log.md)

### Этап 1: Initialization & Data Layer

### Действия ИИ:

- Создан проект WPF.
- Добавлен `appsettings.json`.
- Реализованы полные DTO модели (`Models/`).
- Реализован `GameApiService` с поддержкой SnakeCase и обработкой ошибок.
- Настроен DI контейнер в `App.xaml.cs`.

### Предложенные изменения/артефакты:

- Файл: `Client/Models/TurnRequest.cs`, `Client/Services/GameApiService.cs`, `Client/appsettings.json` ...

### Предложение ИИ для следующего этапа:

- Реализация MVVM архитектуры: MainViewModel, MainWindow.xaml и привязка данных...
