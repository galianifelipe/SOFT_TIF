using System.Diagnostics;

// Ruta al ejecutable de Python
string pythonExe = @"C:\Users\user\AppData\Local\Microsoft\WindowsApps\PythonSoftwareFoundation.Python.3.11_qbz5n2kfra8p0\python.exe ";

// Ruta al script de Python que deseas ejecutar
string scriptPath = @"D:\Escritorio\Prueba\Prueba\Ejecutable.py";

// Crea un nuevo proceso para ejecutar el script de Python
Process process = new Process();
process.StartInfo.FileName = pythonExe;
process.StartInfo.Arguments = scriptPath;
process.StartInfo.UseShellExecute = false;
process.StartInfo.RedirectStandardOutput = true;
process.StartInfo.RedirectStandardError = true;
process.Start();

// Lee la salida y los errores del proceso
string output = process.StandardOutput.ReadToEnd();
string error = process.StandardError.ReadToEnd();

// Cierra el proceso
process.WaitForExit();

// Imprime la salida y los errores
Console.WriteLine(output);
Console.WriteLine(error);