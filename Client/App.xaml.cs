using System.IO;
using System.Windows;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using RolePlayClient.Services;

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
                    // Чтение URL из конфига
                    string baseUrl =
                        context.Configuration["GameApi:BaseUrl"] ?? "http://localhost:8000";

                    // Регистрация HttpClient с BaseAddress
                    services.AddHttpClient<IGameApiService, GameApiService>(client =>
                    {
                        client.BaseAddress = new Uri(baseUrl);
                        client.Timeout = TimeSpan.FromSeconds(30); // Тайм-аут для LLM генерации
                    });

                    // Здесь в будущем будем регистрировать ViewModels и Views
                }
            )
            .Build();

        await _host.StartAsync();

        // 2. Временная проверка связи (Sanity Check)
        await TestConnectionAsync();

        // Открытие главного окна (пока пустого)
        MainWindow = new MainWindow();
        MainWindow.Show();
    }

    private async Task TestConnectionAsync()
    {
        if (_host == null)
            return;

        using var scope = _host.Services.CreateScope();
        var apiService = scope.ServiceProvider.GetRequiredService<IGameApiService>();

        // Временно используем MessageBox, чтобы точно увидеть результат на экране
        try
        {
            bool isConnected = await apiService.CheckHealthAsync();
            if (isConnected)
            {
                MessageBox.Show("✅ SUCCESS: Connected to Backend!", "Connection Test");
            }
            else
            {
                MessageBox.Show(
                    "❌ FAILURE: Backend not reachable.\nCheck if python run.py is running.",
                    "Connection Test"
                );
            }
        }
        catch (Exception ex)
        {
            MessageBox.Show($"❌ ERROR: {ex.Message}", "Connection Test");
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
