using System.Text.Json.Serialization;

namespace RolePlayClient.Models;

// Request DTO
public record TurnRequest(string UserCharacterName, string UserInput);

// Response DTO
public record TurnResponse(
    string AiCharacterName,
    string Motivation,
    string StoryPart,
    List<string> CompletedActions,
    bool IsSuccess = true,
    string? ErrorMessage = null
);

// Health Check DTO
public record HealthCheckResponse(
    string Status,
    string Project,
    Dictionary<string, string> ConfigCheck
);
