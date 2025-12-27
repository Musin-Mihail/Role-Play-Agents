# Журнал разработки: Phase 2 - Desktop Client Implementation (WPF / .NET 10)

Этот документ описывает процесс создания клиента на C# WPF для Role-Play Engine API.

### Контекст (Phase 1 Complete):

- **Backend:** Полностью функционирует на FastAPI (`backend/app/`).
- **API:** Доступно по адресу `http://localhost:8000`.
- **Состояние:** Логика игры и сохранения (`state.json`) полностью на стороне Python.
- **Задача:** Создать графический интерфейс (WPF Client).

### Глобальный план (Roadmap Phase 2):

1.  **Project Setup & Data Layer:**
    - Инициализация проекта на .NET 10 (`net10.0-windows`).
    - Подключение `CommunityToolkit.Mvvm`.
    - Создание C# DTO моделей (`TurnRequest`, `TurnResponse`, `GameState`).
    - Реализация `GameApiService` (HTTP Client).
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
    - Обработка ошибок соединения.

---

### Предложение ИИ для следующего этапа (Этап 1):

**Цель:** Инициализация проекта и слой данных.

- **Создать проект:** `dotnet new wpf -n RolePlayClient -f net10.0-windows`.
- **Добавить пакет:** `dotnet add package CommunityToolkit.Mvvm`.
- **Создать структуру:** `Models/`, `Services/`, `ViewModels/`, `Views/`.
- **Реализовать Models:** Создать `record` классы для `TurnRequest`, `TurnResponse`, `GameState` (зеркально Python-моделям).
- **Реализовать Service:** Класс `GameApiService` для `POST /turn` и `GET /health`.

_Использование .NET 10 и CommunityToolkit.Mvvm обеспечит максимально современный и чистый код._
