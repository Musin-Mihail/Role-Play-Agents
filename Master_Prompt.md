# ЗАДАЧА ДЛЯ ИИ-АРХИТЕКТОРА (PHASE 2: C# WPF CLIENT):

Привет. Мы завершили разработку бэкенда на Python (FastAPI).
Теперь ты выступаешь в роли **Senior C# / WPF Developer**.

Твоя задача — выполнить **Этап 1** создания профессионального десктопного клиента для нашего Role-Play API.

**ТЕКУЩАЯ АРХИТЕКТУРА (BACKEND):**

- **Framework:** FastAPI (запущен на `http://localhost:8000`).
- **Endpoints:**
  - `POST /api/v1/game/turn`: Принимает `TurnRequest`, возвращает `TurnResponse`.
  - `GET /health`: Проверка статуса.
- **Models:** Структура данных описана в Pydantic-моделях бэкенда.
- **JSON Format:** Backend отдает поля в **snake_case** (напр. `user_character_name`), C# использует **PascalCase**. Вложенность JSON (Scene, Characters, Clothing) должна быть полностью соблюдена.

**ЦЕЛЬ ЭТАПА 1 (Initialization & Data Layer):**
Развернуть проект, настроить DI контейнер, HTTP-клиент и создать зеркальные C# DTO модели. Интерфейс (XAML) и ViewModels пока НЕ трогаем.

**ТЕХНОЛОГИЧЕСКИЙ СТЕК:**

- **Language:** C# 12 / .NET 9.
- **Project Type:** WPF Application.
- **Libraries:**
  - `CommunityToolkit.Mvvm` (подготовка для следующего этапа).
  - `Microsoft.Extensions.Hosting` (DI Container).
  - `Microsoft.Extensions.Http` (IHttpClientFactory).
  - `Microsoft.Extensions.Configuration.Json` (appsettings).

**CRITICAL CONSTRAINTS (АРХИТЕКТУРНЫЕ ОГРАНИЧЕНИЯ):**

1.  **Project Structure:**
    - Весь код клиента должен находиться в папке `Client/` (создай её в корне репозитория).
    - Внутренняя структура: `Models/`, `Services/`, `Core/` (для конфигов).
2.  **JSON Handling (System.Text.Json):**
    - Обязательно используй `JsonSerializerOptions`:
      - `PropertyNamingPolicy = JsonNamingPolicy.SnakeCaseLower`.
      - `Converters.Add(new JsonStringEnumConverter())` (Python может отдавать enum как строки).
      - **ВАЖНО:** `UnmappedMemberHandling = JsonUnmappedMemberHandling.Skip`. Клиент НЕ должен падать, если бэкенд пришлет новые поля, которых нет в C# модели.
3.  **DTO Models (Records):**
    - Используй `public record class` для иммутабельности.
    - Структура классов должна зеркально отражать модели Python: `TurnRequest`, `TurnResponse`, `GameState`, `Scene`, `Character`, `InteractiveObject`, `Clothing`, `Relationship`.
    - **Nullability:** Используй **Nullable Reference Types** (`string?`, `int?`). Поля, которые в Python `Optional` (особенно `TurnResponse.error_message` или списки), должны быть nullable.
4.  **Networking:**
    - Реализуй `GameApiService` через `HttpClient` (внедряемый через `IHttpClientFactory`).
    - Base URL должен читаться из `appsettings.json` через `IConfiguration`.
5.  **DI & Entry Point:**
    - Настрой `Host.CreateDefaultBuilder` в `App.xaml.cs`.

**ТВОЙ ПЛАН ДЕЙСТВИЙ:**

1.  **Проанализируй** `Migration_Log.md` (Phase 2).
2.  **Сгенерируй** ответ, сфокусированный на **Слое Данных (Models + Services)** и **Инфраструктуре**.

**ФОРМАТ ОТВЕТА:**

(Краткое обоснование).

## ЧАСТЬ 1: КОД (C# & JSON)

**ПРАВИЛА:**

- Указывай полный путь к файлу (например: `Client/Models/GameState.cs`).
- Включая `App.xaml.cs` с настройкой DI.
- **Full Code Only:** Всегда выдавай полный код файлов.

## ЧАСТЬ 2: ИНСТРУКЦИИ

- Команды для терминала (создание solution и project внутри папки `Client`).
- Итоговая структура папок.

## ЧАСТЬ 3: ПРОВЕРКА (Sanity Check)

- Добавь в `App.xaml.cs` временный метод `private async Task TestConnectionAsync()`, который при запуске приложения (в `OnStartup`):
  1. Запросит сервис `IGameApiService`.
  2. Сделает запрос к `GET /health`.
  3. Выведет результат (успех или ошибку) в `System.Diagnostics.Debug.WriteLine`.
- Это нужно, чтобы мы убедились, что DI и Сеть работают, еще до создания UI.

## ЧАСТЬ 4: ЗАПИСЬ В ЖУРНАЛ (Migration_Log.md)

Обнови лог согласно инструкции в `Migration_Log.md`.
