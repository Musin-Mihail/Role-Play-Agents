# Журнал разработки: Phase 2 - Desktop Client Implementation (WPF / .NET)

Этот документ описывает процесс создания клиента на C# WPF для Role-Play Engine API.

### Контекст (Phase 1 Complete):

- **Backend:** Полностью функционирует на FastAPI (`backend/app/`).
- **API:** Доступно по адресу `http://localhost:8000`.
- **Состояние:** Логика игры и сохранения (`state.json`) полностью на стороне Python.
- **Задача:** Создать графический интерфейс (WPF Client).

### Глобальный план (Roadmap Phase 2):

1.  **Initialization & Data Layer (Current):**
    - Инициализация проекта (.NET 9 WPF) в папке `Client/`.
    - Подключение `CommunityToolkit.Mvvm`, `Microsoft.Extensions.Hosting`, `Microsoft.Extensions.Http`.
    - Настройка `appsettings.json` (Base URL).
    - Создание C# DTO моделей (полное зеркалирование Python моделей, snake_case -> PascalCase, Records).
    - Реализация `GameApiService` с защитой от изменений API (`JsonUnmappedMemberHandling.Skip`).
    - Настройка DI в `App.xaml.cs` и тест соединения.
2.  **MVVM Core & Basic UI:**
    - Создание `MainViewModel`.
    - Верстка `MainWindow.xaml` (Grid layout, input area, output log).
    - Биндинг команд отправки сообщений.
3.  **State Visualization:**
    - Визуализация боковой панели (Инвентарь, Характеристики).
    - Конвертеры данных.
4.  **UX Polish:**
    - Стилизация компонентов.
    - Авто-скролл лога.

---

### Текущий статус: 0 - Initiation

Мы начинаем разработку клиента с нуля.

### Запрос к ИИ (Шаг 1):

**Цель:** Инициализация инфраструктуры и создание слоя данных (API + Models), проверка связи с бэкендом.

**Ожидаемые действия ИИ:**

1.  Создать структуру папок `Client/`.
2.  Сгенерировать DTO (`TurnRequest`, `TurnResponse`, `GameState` и вложенные объекты).
3.  Реализовать `GameApiService` и интерфейс.
4.  Настроить `App.xaml.cs` с DI и временной проверкой соединения (`/health`).

**Предложенные изменения/артефакты:**

- `Client/RolePlayClient.csproj`
- `Client/appsettings.json`
- `Client/Models/*.cs`
- `Client/Services/GameApiService.cs`
- `Client/App.xaml.cs`

### Журнал изменений — Phase 2: Инициализация WPF Клиента

**Действие:** Инициализирована структура проекта C# WPF и слой данных (Data Layer).

**Детали:**

1.  **Настройка проекта:** Создан проект `RolePlayClient` (.NET 9 WPF).
2.  **Зависимости:** Добавлены пакеты `CommunityToolkit.Mvvm`, `Microsoft.Extensions.Hosting`, `Microsoft.Extensions.Http`, `Microsoft.Extensions.Configuration.Json`.
3.  **Слой данных:**
    - Созданы иммутабельные модели (Records) в папке `Models/`, полностью зеркалирующие структуру данных Python-бэкенда.
    - Реализован сервис `GameApiService` через `IHttpClientFactory`.
    - Настроена глобальная конфигурация `System.Text.Json`:
      - Автоматический маппинг `snake_case` (API) ↔ `PascalCase` (C#).
      - Включен `JsonUnmappedMemberHandling.Skip` для защиты клиента от падений при добавлении новых полей в API.
4.  **Инфраструктура:**
    - В `App.xaml.cs` настроен `Generic Host` и DI-контейнер.
    - Реализована проверка соединения (`TestConnectionAsync`) при запуске приложения.

**Текущий статус:** Шаг 1 (Инициализация) завершен.
**Следующий шаг:** Phase 2, Шаг 2 — Реализация ядра MVVM и базового UI (MainViewModel, MainWindow).
