import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def app_folder():
  if getattr(sys, "frozen", False):
    return Path(sys.executable).resolve().parent

  return Path(__file__).resolve().parent


def find_python(root_folder):
  portable_python = root_folder / "portable_python" / "python.exe"

  if portable_python.exists():
    return [str(portable_python)]

  for command in ["py", "python", "python3"]:
    if shutil.which(command):
      return [command]

  print("Python was not found.")
  print(f"Expected portable Python at: {portable_python}")
  print("Or install Python normally and make sure py/python is available.")
  sys.exit(1)


def add_binary_args(command, source, destination):
  if not source.exists():
    return

  command.extend([
    "--add-binary",
    f"{source}{';'}{destination}",
  ])


def add_data_args(command, source, destination):
  if not source.exists():
    return

  command.extend([
    "--add-data",
    f"{source}{';'}{destination}",
  ])


def main(program):
  root_folder = app_folder()
  program_path = (root_folder / program).resolve()

  if not program_path.exists():
    print(f"Script file does not exist: {program_path}")
    sys.exit(1)

  python_command = find_python(root_folder)
  portable_folder = root_folder / "portable_python"
  portable_dlls = portable_folder / "DLLs"
  portable_tcl = portable_folder / "tcl"

  dist_folder = root_folder / "dist"
  build_folder = Path(tempfile.gettempdir()) / "dbd_slot_machine_pyinstaller_build"
  spec_folder = Path(tempfile.gettempdir()) / "dbd_slot_machine_pyinstaller_spec"

  shutil.rmtree(build_folder, ignore_errors=True)
  shutil.rmtree(spec_folder, ignore_errors=True)

  build_folder.mkdir(parents=True, exist_ok=True)
  spec_folder.mkdir(parents=True, exist_ok=True)
  dist_folder.mkdir(parents=True, exist_ok=True)

  print("Building executable...")
  print(f"Project folder: {root_folder}")
  print(f"Python command: {' '.join(python_command)}")
  print(f"Script: {program_path}")
  print(f"Build folder: {build_folder}")
  print(f"Spec folder: {spec_folder}")

  command = python_command + [
    "-m",
    "PyInstaller",
    "--onefile",
    "--noconsole",
    "--clean",
    "--noconfirm",
    "--collect-all",
    "PIL",
    "--collect-binaries",
    "PIL",
    "--collect-data",
    "PIL",
    "--hidden-import",
    "PIL",
    "--hidden-import",
    "PIL.Image",
    "--hidden-import",
    "PIL.ImageTk",
    "--hidden-import",
    "PIL._imaging",
    "--hidden-import",
    "PIL._imagingtk",
    "--hidden-import",
    "PIL._tkinter_finder",
    "--distpath",
    str(dist_folder),
    "--workpath",
    str(build_folder),
    "--specpath",
    str(spec_folder),
  ]

  add_binary_args(command, portable_dlls, "DLLs")
  add_data_args(command, portable_tcl, "tcl")

  command.append(str(program_path))

  result = subprocess.run(command, cwd=root_folder)

  if result.returncode != 0:
    print("Build failed.")
    sys.exit(result.returncode)

  output_file = dist_folder / f"{program_path.stem}.exe"
  print(f"Build complete: {output_file}")


if __name__ == "__main__":
  args = sys.argv[1:]

  if not args:
    print("Usage: packager.exe spinthewheel.py")
    sys.exit(1)

  main(args[0])
