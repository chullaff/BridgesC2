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

    if not agent_script.exists():
        print("Agent template not found.")
        return

    with tempfile.TemporaryDirectory() as tmpdir:
        build_path = Path(tmpdir)

        # Копируем шаблон агента
        shutil.copytree(template_dir, build_path, dirs_exist_ok=True)

        # Создаём config.py
        config_file = build_path / "config.py"
        with open(config_file, "w") as f:
            f.write(f'SERVER_URL = "{SERVER_URL}"\n')
            f.write(f'AGENT_NAME = "{name}"\n')

        # Обфускация с PyArmor
        obf_dir = build_path / "obf"
        try:
            subprocess.run([
                "pyarmor", "gen",
                "--output", str(obf_dir),
                "--with-runtime",
                str(build_path / "agent.py")
            ], check=True)
        except subprocess.CalledProcessError:
            print("[!] Obfuscation failed.")
            return

        # PyInstaller: сборка в EXE
        try:
            subprocess.run([
                "pyinstaller", "--onefile", "--noconfirm",
                "--log-level=ERROR",
                "--name", output,
                str(obf_dir / "agent.py")
            ], check=True)
        except subprocess.CalledProcessError:
            print("[!] PyInstaller build failed.")
            return

        print(f"[+] Агент собран как EXE: dist/{output}.exe")
