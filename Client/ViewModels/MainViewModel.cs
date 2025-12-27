using System.Text;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using RolePlayClient.Models;
using RolePlayClient.Services;

namespace RolePlayClient.ViewModels;

public partial class MainViewModel : ObservableObject
{
    private readonly IGameApiService _gameApiService;

    [ObservableProperty]
    private string _userInput = string.Empty;

    [ObservableProperty]
    private string _storyLog =
        "Welcome to the Role-Play Client.\nEnsure the Backend is running and wait for connection...\n";

    [ObservableProperty]
    private bool _isBusy;

    [ObservableProperty]
    private string _statusMessage = "Ready";

    public MainViewModel(IGameApiService gameApiService)
    {
        _gameApiService = gameApiService;
    }

    [RelayCommand]
    private async Task SendTurnAsync()
    {
        if (string.IsNullOrWhiteSpace(UserInput))
            return;

        IsBusy = true;
        StatusMessage = "Processing turn...";

        // 1. Отображаем ввод пользователя в логе
        AppendToLog($"USER: {UserInput}");

        var currentInput = UserInput;
        UserInput = string.Empty; // Очистка поля ввода

        try
        {
            // 2. Формируем запрос
            // Примечание: UserCharacterName пока хардкодим как "Sveta" для MVP,
            // позже это будет браться из настроек или выбора персонажа.
            var request = new TurnRequest("Sveta", currentInput);

            // 3. Отправляем на сервер
            var response = await _gameApiService.SendTurnAsync(request);

            if (response != null && response.IsSuccess)
            {
                // 4. Отображаем ответ ИИ
                AppendToLog($"AI ({response.AiCharacterName}): {response.StoryPart}");

                if (response.CompletedActions.Count > 0)
                {
                    AppendToLog($"[Actions: {string.Join(", ", response.CompletedActions)}]");
                }

                StatusMessage = "Turn completed.";
            }
            else
            {
                var error = response?.ErrorMessage ?? "Unknown error";
                AppendToLog($"SYSTEM ERROR: {error}");
                StatusMessage = "Error occurred.";
            }
        }
        catch (Exception ex)
        {
            AppendToLog($"CLIENT ERROR: {ex.Message}");
            StatusMessage = "Connection failed.";
        }
        finally
        {
            IsBusy = false;
        }
    }

    private void AppendToLog(string message)
    {
        var sb = new StringBuilder(StoryLog);
        if (sb.Length > 0)
            sb.AppendLine();
        sb.AppendLine(new string('-', 20));
        sb.AppendLine(message);
        StoryLog = sb.ToString();
    }
}
