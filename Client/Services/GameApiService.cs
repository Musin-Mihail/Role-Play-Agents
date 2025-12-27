using System.Net.Http;
using System.Net.Http.Json;
using System.Text.Json;
using System.Text.Json.Serialization;
using Microsoft.Extensions.Logging;
using RolePlayClient.Models;

namespace RolePlayClient.Services;

public class GameApiService : IGameApiService
{
    private readonly HttpClient _httpClient;
    private readonly ILogger<GameApiService> _logger;
    private readonly JsonSerializerOptions _jsonOptions;

    public GameApiService(HttpClient httpClient, ILogger<GameApiService> logger)
    {
        _httpClient = httpClient;
        _logger = logger;

        // CRITICAL: Настройка совместимости с Python/FastAPI
        _jsonOptions = new JsonSerializerOptions
        {
            PropertyNamingPolicy = JsonNamingPolicy.SnakeCaseLower, // user_input -> UserInput
            UnmappedMemberHandling = JsonUnmappedMemberHandling.Skip, // Игнорировать новые поля бэкенда
            Converters = { new JsonStringEnumConverter() },
            PropertyNameCaseInsensitive = true,
        };
    }

    public async Task<bool> CheckHealthAsync()
    {
        try
        {
            var response = await _httpClient.GetAsync("/health");
            if (response.IsSuccessStatusCode)
            {
                var content = await response.Content.ReadFromJsonAsync<HealthCheckResponse>(
                    _jsonOptions
                );
                _logger.LogInformation(
                    $"API Health: {content?.Status} (Project: {content?.Project})"
                );
                return true;
            }
            _logger.LogWarning($"API Health check failed: {response.StatusCode}");
            return false;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "API Connection failed.");
            return false;
        }
    }

    public async Task<TurnResponse?> SendTurnAsync(TurnRequest request)
    {
        try
        {
            var response = await _httpClient.PostAsJsonAsync(
                "/api/v1/game/turn",
                request,
                _jsonOptions
            );
            response.EnsureSuccessStatusCode();

            return await response.Content.ReadFromJsonAsync<TurnResponse>(_jsonOptions);
        }
        catch (HttpRequestException ex)
        {
            _logger.LogError(ex, "Error sending turn request.");
            return new TurnResponse(
                AiCharacterName: "System",
                Motivation: "Error",
                StoryPart: "Failed to communicate with the server.",
                CompletedActions: [],
                IsSuccess: false,
                ErrorMessage: ex.Message
            );
        }
    }
}
