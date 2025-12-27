# ЗАДАЧА ДЛЯ ИИ-АРХИТЕКТОРА (PHASE 2: C# WPF CLIENT):

Привет. Мы завершили разработку бэкенда на Python (FastAPI).
Теперь ты выступаешь в роли **Senior C# / WPF Developer**.

Твоя задача — создать профессиональный десктопный клиент для взаимодействия с нашим Role-Play API.

**ТЕКУЩАЯ АРХИТЕКТУРА (BACKEND):**

- **Framework:** FastAPI (запущен на `http://localhost:8000`).
- **Endpoints:**
  - `POST /api/v1/game/turn`: Принимает JSON (user_input), возвращает JSON (story, updates).
  - `GET /health`: Проверка статуса.
- **Models:** Структура данных описана в Pydantic-моделях бэкенда (см. `backend/app/models/`).

**ЦЕЛЬ ФАЗЫ 2:**
Разработать WPF-приложение (Desktop), реализующее паттерн **MVVM**. Приложение должно быть красивым, отзывчивым и готовым к масштабированию.

**ТЕХНОЛОГИЧЕСКИЙ СТЕК:**

- **Language:** C# 14 (.NET 10).
- **Framework:** WPF (Windows Presentation Foundation).
- **Pattern:** MVVM (Model-View-ViewModel).
  - Используй `CommunityToolkit.Mvvm` (Modern standard) для чистоты кода (RelayCommand, ObservableProperty).
- **Networking:** `HttpClient` + `System.Net.Http.Json`.
- **Serialization:** `System.Text.Json`.

**CRITICAL CONSTRAINTS (АРХИТЕКТУРНЫЕ ОГРАНИЧЕНИЯ):**

1.  **Strict MVVM:** Никакого бизнес-кода в `MainWindow.xaml.cs`. Вся логика — во ViewModels.
2.  **Async/Await:** Все сетевые запросы строго асинхронны. UI не должен зависать.
3.  **Typed Models:** C# классы (Records) должны зеркально отражать Python модели. Используй `record` для DTO, где это уместно.
4.  **Target Framework:** Указывай `<TargetFramework>net10.0-windows</TargetFramework>` в csproj.
5.  **Full Code Only:** Всегда выдавай полный код файлов.

**ТВОЙ ПЛАН ДЕЙСТВИЙ:**

1.  **Проанализируй** `Migration_Log.md` (Phase 2).
2.  **Сгенерируй** ответ из четырех частей.

**ФОРМАТ ОТВЕТА:**

(Краткое обоснование).

## ЧАСТЬ 1: КОД (C# & XAML)

**ПРАВИЛА:**

- Указывай путь к файлу (например: `Client/Services/GameApiService.cs`).
- Предоставляй ВЕСЬ код.

## ЧАСТЬ 2: ИНСТРУКЦИИ

- Команды для терминала (dotnet new, dotnet add package).

## ЧАСТЬ 3: ПРОВЕРКА

- Критерии проверки работоспособности этапа.

## ЧАСТЬ 4: ЗАПИСЬ В ЖУРНАЛ (Migration_Log.md)

### Этап X: {Название этапа}

### Действия ИИ:

- {Список}

### Предложенные изменения/артефакты:

- Файл: ...

### Предложение ИИ для следующего этапа:

- ...
