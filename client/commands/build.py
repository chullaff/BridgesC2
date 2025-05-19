import os
import shutil
import subprocess

def cmd_build(os_name: str, name: str, output: str):
    """
    Собирает микроагента под указанную ОС.
    Пока реализовано только для Windows.
    """
    os_name = os_name.lower()
    if os_name != "windows":
        print(f"Build for OS '{os_name}' is not supported yet.")
        return

    # Путь к шаблону агента Windows
    template_dir = os.path.join(os.path.dirname(__file__), "..", "..", "agent_template", "windows")
    agent_script = os.path.join(template_dir, "agent.py")

    if not os.path.exists(agent_script):
        print("Agent template for Windows not found.")
        return

    # Создаём временную директорию для сборки
    build_dir = os.path.join(template_dir, "build_temp")
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)
    os.makedirs(build_dir)

    # Копируем шаблон агента в build_temp
    shutil.copy(agent_script, build_dir)

    # Пишем конфигурационный файл с параметрами агента (например, имя и адрес сервера)
    config_path = os.path.join(build_dir, "config.py")
    with open(config_path, "w") as f:
        f.write(f'SERVER_URL = "http://127.0.0.1:8000"\n')
        f.write(f'AGENT_NAME = "{name}"\n')

    # Собираем исполняемый файл с помощью PyInstaller
    # Нужно, чтобы pyinstaller был установлен в окружении
    try:
        subprocess.run([
            "pyinstaller",
            "--onefile",
            "--name", output,
            "--log-level=ERROR",  # минимизируем логи PyInstaller
            os.path.join(build_dir, "agent.py")
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)  # подавляем вывод
    except subprocess.CalledProcessError:
        print("Failed to build agent executable.")
        return

    dist_path = os.path.join(build_dir, "dist", output + (".exe" if not output.endswith(".exe") else ""))
    if os.path.exists(dist_path):
        # Копируем итоговый exe в текущую директорию
        shutil.copy(dist_path, os.path.join(os.getcwd(), output))
        print(f'[+] Micro-agent "{name}" built for Windows: {output}')
    else:
        print("Build succeeded but executable not found.")

    # Чистим временные файлы PyInstaller
    shutil.rmtree(build_dir, ignore_errors=True)
    spec_file = output + ".spec"
    if os.path.exists(spec_file):
        os.remove(spec_file)
