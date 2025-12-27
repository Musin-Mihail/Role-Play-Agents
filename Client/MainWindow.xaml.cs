using System.Windows;
using RolePlayClient.ViewModels;

namespace RolePlayClient;

/// <summary>
/// Interaction logic for MainWindow.xaml
/// </summary>
public partial class MainWindow : Window
{
    // Внедрение ViewModel через конструктор
    public MainWindow(MainViewModel viewModel)
    {
        InitializeComponent();
        DataContext = viewModel;
    }
}
