using System.IO;
using System.Windows;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using RolePlayClient.Services;
using RolePlayClient.ViewModels;

namespace RolePlayClient;

public partial class App : Application
{
    private IHost? _host;

    public App() { }

    protected override async void OnStartup(StartupEventArgs e)
    {
        base.OnStartup(e);

        // 1. Создание и настройка Хоста
        _host = Host.CreateDefaultBuilder()
            .ConfigureAppConfiguration(
                (context, config) =>
                {
                    config.SetBasePath(Directory.GetCurrentDirectory());
                    config.AddJsonFile("appsettings.json", optional: false, reloadOnChange: true);
                }
            )
            .ConfigureServices(
                (context, services) =>
                {
                    // --- Configuration ---
                    string baseUrl =
                        context.Configuration["GameApi:BaseUrl"] ?? "http://localhost:8000";

                    // --- Services ---
                    services.AddHttpClient<IGameApiService, GameApiService>(client =>
                    {
                        client.BaseAddress = new Uri(baseUrl);
                        client.Timeout = TimeSpan.FromSeconds(60); // Увеличиваем тайм-аут для генерации LLM
                    });

                    // --- ViewModels ---
                    services.AddSingleton<MainViewModel>();

                    // --- Windows ---
                    // Регистрируем MainWindow, чтобы DI мог внедрить в него MainViewModel
                    services.AddSingleton<MainWindow>();
                }
            )
            .Build();

        await _host.StartAsync();

        // 2. Временная проверка связи (Sanity Check)
        // Можно оставить или убрать, так как теперь у нас есть UI для проверки
        // await TestConnectionAsync();

        // 3. Запуск Главного Окна через DI
        var mainWindow = _host.Services.GetRequiredService<MainWindow>();
        mainWindow.Show();
    }

    private async Task TestConnectionAsync()
    {
        if (_host == null)
            return;

        using var scope = _host.Services.CreateScope();
        var apiService = scope.ServiceProvider.GetRequiredService<IGameApiService>();

        try
        {
            // Просто пишем в Debug, чтобы не блокировать запуск UI лишними окнами
            bool isConnected = await apiService.CheckHealthAsync();
            System.Diagnostics.Debug.WriteLine(
                isConnected ? "✅ Connection Test Passed" : "❌ Connection Test Failed"
            );
        }
        catch (Exception ex)
        {
            System.Diagnostics.Debug.WriteLine($"❌ Connection Error: {ex.Message}");
        }
    }

    protected override async void OnExit(ExitEventArgs e)
    {
        if (_host != null)
        {
            await _host.StopAsync();
            _host.Dispose();
        }
        base.OnExit(e);
    }
}
