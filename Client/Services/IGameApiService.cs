using RolePlayClient.Models;

namespace RolePlayClient.Services;

public interface IGameApiService
{
    Task<bool> CheckHealthAsync();
    Task<TurnResponse?> SendTurnAsync(TurnRequest request);
}
