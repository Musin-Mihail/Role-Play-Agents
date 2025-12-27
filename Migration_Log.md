# Журнал разработки: Phase 2 - Desktop Client Implementation (WPF / .NET)

Этот документ описывает процесс создания клиента на C# WPF для Role-Play Engine API.

### Контекст (Phase 1 Complete):

- **Backend:** Полностью функционирует на FastAPI (`backend/app/`).
- **API:** Доступно по адресу `http://localhost:8000`.
- **Состояние:** Логика игры и сохранения (`state.json`) полностью на стороне Python.
- **Задача:** Создать графический интерфейс (WPF Client).

### Глобальный план (Roadmap Phase 2):

1.  **Project Setup & Data Layer:**
    - Инициализация проекта (.NET 9 WPF).
    - Подключение `CommunityToolkit.Mvvm`, `Microsoft.Extensions.Hosting`, `Microsoft.Extensions.Http`.
    - Настройка `appsettings.json` (Base URL).
    - Создание C# DTO моделей (полное зеркалирование Python моделей, snake_case -> PascalCase, Records).
    - Реализация `GameApiService` (IHttpClientFactory).
    - Настройка DI в `App.xaml.cs`.
2.  **MVVM Core & Basic UI:**
    - Создание `MainViewModel`.
    - Верстка `MainWindow.xaml` (Grid layout, input area, output log).
    - Биндинг команд отправки сообщений.
3.  **State Visualization:**
    - Визуализация боковой панели (Инвентарь, Характеристики).
    - Конвертеры данных (например, `BoolToVisibilityConverter`).
4.  **UX Polish:**
    - Стилизация компонентов (Resources/Styles).
    - Авто-скролл лога сообщений.
    - Обработка ошибок соединения (Retry policies).

---

### Предложение ИИ для следующего этапа (Этап 1):

**Цель:** Инициализация проекта, инфраструктура DI и слой данных (API + Models).

- **Создать проект:** `dotnet new wpf -n RolePlayClient`.
- **Добавить пакеты:**
  - `CommunityToolkit.Mvvm`
  - `Microsoft.Extensions.Hosting`
  - `Microsoft.Extensions.Http`
- **Создать структуру:** `Models/`, `Services/` (папки `ViewModels` и `Views` создадим на следующем этапе).
- **Реализовать Models (DTO):** Создать `public record class` для:
  - `TurnRequest`, `TurnResponse`.
  - `GameState`, `Character`, `Scene`, `InteractiveObject`, `Clothing`.
  - Учесть Nullable типы (`string?`, `List<string>?`) для корректной десериализации.
- **Реализовать Service:** Класс `GameApiService` (и интерфейс `IGameApiService`) с настройкой `JsonNamingPolicy.SnakeCaseLower` и `JsonStringEnumConverter`.
- **Настроить App.xaml.cs:** Внедрение зависимостей (DI), регистрация `HttpClient` и чтение конфигурации из `appsettings.json`.
