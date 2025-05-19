import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from shared.config import SERVER_URL


def cmd_build(os_name: str, name: str, output: str):
    os_name = os_name.lower()
    if os_name != "windows":
        print(f"Build for OS '{os_name}' is not supported yet.")
        return

    template_dir = Path(__file__).parent.parent.parent / "agent_template" / "windows"
    agent_script = template_dir / "agent.py"
    shared_dir = template_dir / "utils"
    config_file = shared_dir / "config.py"

    if not agent_script.exists():
        print("Agent template not found.")
        return

    # Обновляем config.py прямо в shared/
    shared_dir.mkdir(parents=True, exist_ok=True)
    with open(config_file, "w") as f:
        f.write(f'SERVER_URL = "{SERVER_URL}"\n')
        f.write(f'AGENT_NAME = "{name}"\n')

    print("[*] Собираем агент с помощью PyInstaller...")

    try:
        subprocess.run([
            "pyinstaller",
            "--onefile",
            "--noconfirm",
            "--log-level=ERROR",
            "--name", output,
            "--add-data", f"{shared_dir}{os.pathsep}utils",
            str(agent_script)
        ], cwd=template_dir, check=True)
    except subprocess.CalledProcessError as e:
        print(f"[!] Ошибка сборки PyInstaller: {e}")
        return

    # Переносим .exe
    dist_dir = Path("dist")
    dist_dir.mkdir(exist_ok=True)
    built_exe = template_dir / "dist" / output
    if not built_exe.exists():
        print(f"[!] Не найден собранный агент: {built_exe}")
        return

    shutil.copy(built_exe, dist_dir / output)
    print(f"[+] Агент собран: dist/{output}")

    # os_name = os_name.lower()
    # if os_name != "windows":
    #     print(f"Build for OS '{os_name}' is not supported yet.")
    #     return

    # template_dir = Path(__file__).parent.parent.parent / "agent_template" / "windows"
    # agent_script = template_dir / "agent.py"

    # if not agent_script.exists():
    #     print("Agent template not found.")
    #     return

    # with tempfile.TemporaryDirectory() as tmpdir:
    #     tmp_path = Path(tmpdir)
    #     build_script = tmp_path / "agent.py"
    #     shutil.copy(agent_script, build_script)

    #     # Копируем зависимости
    #     for subdir in ["comms", "crypto", "shared"]:
    #         src = template_dir / subdir
    #         dst = tmp_path / subdir
    #         if src.exists():
    #             shutil.copytree(src, dst)

    #     # Создаём config.py
    #     config_file = tmp_path / "shared" / "config.py"
    #     print(config_file)
    #     config_file.parent.mkdir(exist_ok=True, parents=True)
    #     with open(config_file, "w") as f:
    #         f.write(f'SERVER_URL = "{SERVER_URL}"\n')
    #         f.write(f'AGENT_NAME = "{name}"\n')
    #         f.readlines()

    #     print("[*] Собираем агент с помощью PyInstaller...")

    #     try:
    #         subprocess.run([
    #             "pyinstaller",
    #             "--onefile",
    #             "--noconfirm",
    #             "--log-level=ERROR",
    #             "--hidden-import=requests",
    #             "--hidden-import=socket",
    #             "--hidden-import=threading",
    #             "--hidden-import=asyncio",
    #             "--name", output, f'{(tmp_path / 'shared')}{os.pathsep}shared',
    #             str(build_script)
    #         ], cwd=tmp_path, check=True)
    #     except subprocess.CalledProcessError as e:
    #         print(f"[!] Ошибка сборки PyInstaller: {e}")
    #         return

    #     # Переносим готовый .exe
    #     dist_dir = Path("dist")
    #     dist_dir.mkdir(exist_ok=True)
    #     built_exe = tmp_path / "dist" / output
    #     if not built_exe.exists():
    #         print(f"[!] Не найден собранный агент: {built_exe}")
    #         return

    #     shutil.copy(built_exe, dist_dir / output)
    #     print(f"[+] Агент собран: dist/{output}")
    #     print("[!] Запуск на целевой системе: просто двойной клик или `./agent.exe`")
