import subprocess
import sys
from pathlib import Path

PORTABLE_FOLDER_NAME = "portable_python"
PORTABLE_PYTHON_EXE = "python.exe"
DEFAULT_SCRIPT_NAME = "spinthewheel.py"


def app_folder():
  if getattr(sys, "frozen", False):
    return Path(sys.executable).resolve().parent

  return Path(__file__).resolve().parent


def portable_folder():
  return app_folder() / PORTABLE_FOLDER_NAME


def portable_python_path():
  return portable_folder() / PORTABLE_PYTHON_EXE


def run_command(command, cwd):
  completed = subprocess.run(command, cwd=cwd)

  if completed.returncode != 0:
    raise SystemExit(completed.returncode)


def ensure_script_exists(script_path):
  if not script_path.exists():
    print(f"Script file does not exist: {script_path}")
    raise SystemExit(1)

  if script_path.suffix.lower() != ".py":
    print(f"Expected a .py file, but got: {script_path}")
    raise SystemExit(1)


def ensure_portable_python_exists(python_exe):
  if python_exe.exists():
    return

  print("Portable Python was not found.")
  print()
  print(f"Expected: {python_exe}")
  print()
  print("Place a Windows portable Python environment in the portable_python folder")
  print("with PyInstaller installed, then run this packager again.")
  raise SystemExit(1)


def ensure_pyinstaller_available(python_exe):
  check_command = [str(python_exe), "-m", "PyInstaller", "--version"]
  completed = subprocess.run(
    check_command,
    cwd=app_folder(),
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL
  )

  if completed.returncode == 0:
    return

  print("PyInstaller is not available in portable_python.")
  print()
  print("Install PyInstaller into the bundled portable Python environment,")
  print("then run this packager again.")
  print()
  print("Expected command to work:")
  print(f"  {python_exe} -m PyInstaller --version")
  raise SystemExit(1)


def resolve_script_path(args):
  if args:
    script_path = Path(args[0])
    if not script_path.is_absolute():
      script_path = app_folder() / script_path
    return script_path.resolve()

  return (app_folder() / DEFAULT_SCRIPT_NAME).resolve()


def build_exe(script_path):
  python_exe = portable_python_path()

  ensure_script_exists(script_path)
  ensure_portable_python_exists(python_exe)
  ensure_pyinstaller_available(python_exe)

  output_name = script_path.stem

  command = [
    str(python_exe),
    "-m",
    "PyInstaller",
    "--onefile",
    "--noconsole",
    "--clean",
    "--name",
    output_name,
    str(script_path)
  ]

  print("Building executable with bundled portable Python...")
  print(f"Project folder: {app_folder()}")
  print(f"Python: {python_exe}")
  print(f"Script: {script_path}")
  print()

  run_command(command, cwd=app_folder())

  print()
  print("Build complete.")
  print(f"Executable should be in: {app_folder() / 'dist'}")


def main():
  script_path = resolve_script_path(sys.argv[1:])
  build_exe(script_path)


if __name__ == "__main__":
  main()