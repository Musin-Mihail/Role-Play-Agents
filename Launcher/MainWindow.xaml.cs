using System.Diagnostics;
using System.IO;
using System.Text;
using System.Windows;

namespace Launcher
{
    public partial class MainWindow : Window
    {
        private Process? _pythonProcess;
        private StreamWriter? _processInput;

        public MainWindow()
        {
            InitializeComponent();
            StartPythonGame();
        }

        private void StartPythonGame()
        {
            string projectRoot = @"D:\Repositories\Role-Play-Agents";

            _pythonProcess = new Process();
            _pythonProcess.StartInfo.FileName = "python";
            _pythonProcess.StartInfo.Arguments = "-u \"main.py\""; // Теперь можно указывать просто имя файла

            // КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ:
            _pythonProcess.StartInfo.WorkingDirectory = projectRoot;

            _pythonProcess.StartInfo.UseShellExecute = false;
            _pythonProcess.StartInfo.RedirectStandardOutput = true;
            _pythonProcess.StartInfo.RedirectStandardInput = true;
            _pythonProcess.StartInfo.RedirectStandardError = true;
            _pythonProcess.StartInfo.CreateNoWindow = true;

            _pythonProcess.OutputDataReceived += (s, e) => AppendLog(e.Data);
            _pythonProcess.ErrorDataReceived += (s, e) => AppendLog("[ERROR] " + e.Data);

            _pythonProcess.Start();
            _processInput = _pythonProcess.StandardInput;

            _pythonProcess.BeginOutputReadLine();
            _pythonProcess.BeginErrorReadLine();
        }

        private void AppendLog(string? text)
        {
            if (string.IsNullOrEmpty(text)) return;

            // Вывод в UI поток
            Dispatcher.Invoke(() =>
            {
                LogTextBox.AppendText(text + Environment.NewLine);
                LogTextBox.ScrollToEnd();
            });
        }

        private void SendButton_Click(object sender, RoutedEventArgs e)
        {
            string input = UserInputTextBox.Text;
            if (!string.IsNullOrEmpty(input) && _processInput != null)
            {
                _processInput.WriteLine(input); // Отправка в Python (input())
                AppendLog($"> {input}");        // Дублирование в лог
                UserInputTextBox.Clear();
            }
        }

        protected override void OnClosed(EventArgs e)
        {
            if (_pythonProcess != null && !_pythonProcess.HasExited)
            {
                _pythonProcess.Kill(); // Завершаем процесс при закрытии окна
            }
            base.OnClosed(e);
        }
    }
}