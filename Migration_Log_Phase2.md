# Журнал разработки: Phase 2 - Desktop Client Implementation (WPF / .NET)

Этот документ описывает процесс создания клиента на C# WPF для Role-Play Engine API.

### Контекст (Phase 1 Complete):

- **Backend:** Полностью функционирует на FastAPI (`backend/app/`).
- **API:** Доступно по адресу `http://localhost:8001`.
- **Состояние:** Логика игры и сохранения (`state.json`) полностью на стороне Python.
- **Задача:** Создать графический интерфейс (WPF Client).

### Глобальный план (Roadmap Phase 2):

1.  **Initialization & Data Layer:**
    - Инициализация проекта (.NET 9 WPF) в папке `Client/`.
    - Подключение `CommunityToolkit.Mvvm`, `Microsoft.Extensions.Hosting`, `Microsoft.Extensions.Http`.
    - Создание C# DTO моделей (полное зеркалирование Python моделей, snake_case -> PascalCase, Records).
    - Реализация `GameApiService` с защитой от изменений API (`JsonUnmappedMemberHandling.Skip`).
    - Настройка DI в `App.xaml.cs` и тест соединения.
2.  **MVVM Core & Basic UI:**
    - Создание `MainViewModel` (ядро логики UI).
    - Верстка `MainWindow.xaml` (Grid layout, input area, output log).
    - Биндинг команд отправки сообщений.
3.  **State Visualization:**
    - Визуализация боковой панели (Инвентарь, Характеристики).
    - Конвертеры данных (BooleanToVisibility, TextFormatting).
4.  **UX Polish:**
    - Стилизация компонентов.
    - Авто-скролл лога.
    - Обработка ошибок (Pop-up уведомления).

---

### Текущий статус: Phase 2, Step 1 — Completed

Мы успешно инициализировали проект клиента и настроили слой данных. Приложение запускается, DI-контейнер работает, связь с API проверена.

### Журнал изменений (Шаг 1: Инициализация и Data Layer)

**Цель:** Развернуть архитектуру приложения, подключить библиотеки и научить клиент "понимать" данные бэкенда.

**1. Инфраструктура проекта (`Client/RolePlayClient.csproj`, `App.xaml.cs`):**

- Создан WPF проект на .NET 9 (Preview/RC) или .NET 8 (LTS).
- Добавлены ключевые NuGet пакеты:
  - `CommunityToolkit.Mvvm` (для будущих ViewModels).
  - `Microsoft.Extensions.Hosting` (для Dependency Injection).
  - `Microsoft.Extensions.Http` (для IHttpClientFactory).
  - `Microsoft.Extensions.Configuration.Json` (для appsettings).
- В `App.xaml.cs` настроен `Host.CreateDefaultBuilder`:
  - Внедрение зависимостей (DI).
  - Чтение конфигурации из `appsettings.json`.
  - Реализован метод `TestConnectionAsync` для проверки доступности бэкенда при старте.

**2. Конфигурация (`Client/appsettings.json`):**

- Добавлен файл настроек для хранения `BaseUrl` API.

**3. Модели данных (`Client/Models/*.cs`):**

- Созданы `Record`-типы для иммутабельности данных.
- Полностью перенесены структуры из Python (`GameState`, `Character`, `Scene`, `TurnRequest`, `TurnResponse`).
- Соблюдена вложенность объектов (`Clothing`, `InteractiveObject`, `Relationship`).

**4. Сервисный слой (`Client/Services/GameApiService.cs`):**

- Реализован типизированный HTTP-клиент.
- Настроена `JsonSerializerOptions`:
  - `PropertyNamingPolicy = JsonNamingPolicy.SnakeCaseLower` (автоматическая конвертация `user_input` -> `UserInput`).
  - `JsonUnmappedMemberHandling.Skip` (защита от падений при добавлении новых полей на бэкенде).
- Реализованы методы:
  - `CheckHealthAsync()` — проверка статуса сервера.
  - `SendTurnAsync()` — отправка хода и получение ответа.

---

**Следующий шаг:** Переход к Шагу 2 (MVVM Core & Basic UI). Создание ViewModel и верстка основного окна.

### Журнал изменений (Шаг 2: MVVM Core & Basic UI)

**Цель:** Реализация паттерна MVVM, создание ViewModel и базового пользовательского интерфейса для взаимодействия с API.

**1. ViewModel (`Client/ViewModels/MainViewModel.cs`):**

- Создан класс `MainViewModel`, наследующий `ObservableObject` (CommunityToolkit.Mvvm).
- Реализованы Observable свойства:
  - `UserInput` (строка ввода).
  - `StoryLog` (текстовое поле для истории).
  - `IsBusy` (блокировка UI во время запроса).
  - `StatusMessage` (статус строка).
- Реализована команда `SendTurnCommand` (AsyncRelayCommand):
  - Отправляет `TurnRequest` через `IGameApiService`.
  - Обновляет лог ответом от ИИ или сообщением об ошибке.

**2. UI (`Client/MainWindow.xaml`):**

- Создана разметка Grid:
  - Область прокрутки (`ScrollViewer`) для чтения истории.
  - Поле ввода (`TextBox`) и кнопка отправки (`Button`).
  - Статус бар с прогресс-баром.
- Настроен DataBinding к свойствам ViewModel.
- Добавлен `InverseBooleanConverter` для блокировки ввода во время ожидания ответа сервера.

**3. Интеграция (`App.xaml.cs`, `MainWindow.xaml.cs`):**

- `MainViewModel` зарегистрирована в DI контейнере как Singleton.
- `MainWindow` теперь получает `MainViewModel` через конструктор (Constructor Injection).
- В `App.xaml.cs` изменена логика запуска: окно разрешается через `host.Services.GetRequiredService<MainWindow>()`.

**Текущий статус:** Phase 2, Step 2 — Completed.
**Следующий шаг:** Phase 2, Step 3 — State Visualization (Боковая панель, Инвентарь, Характеристики).
