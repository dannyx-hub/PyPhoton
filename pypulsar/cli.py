from __future__ import annotations
import os
import shutil
import subprocess
import sys
from pathlib import Path
import typer
from typing import Optional

app = typer.Typer(
    name="PyPulsar",
    help="Modern Python desktop framework - lightweight, secure and build in python",
    add_completion=False,
    no_args_is_help=True
)
TEMPLATES_DIR = Path(__file__).parent / "templates"


@app.command()
def create(
    name: str = typer.Argument(..., help="Name of the new project"),
    template: str = typer.Option(
        "basic", "--template", "-t", help="Template to use: basic, vue, react, svelte"
    ),
):
    project_dir = Path(name)

    if project_dir.exists():
        typer.secho(f"Project '{name}' already exists!", fg=typer.colors.RED, err=True)
        raise typer.Exit(1)

    template_dir = TEMPLATES_DIR / template
    if not template_dir.exists() or not template_dir.is_dir():
        typer.secho(f"Template '{template}' not found!", fg=typer.colors.RED, err=True)
        available = [p.name for p in TEMPLATES_DIR.iterdir() if p.is_dir()]
        typer.echo(f"Available templates: {', '.join(sorted(available))}")
        raise typer.Exit(1)

    typer.secho(f"Creating project '{name}' from template '{template}'...", fg=typer.colors.CYAN)

    shutil.copytree(template_dir, project_dir, dirs_exist_ok=True)

    main_py = project_dir / "main.py"
    if main_py.exists():
        try:
            content = main_py.read_text(encoding="utf-8")
            content = content.replace("PyPulsar App", name.replace("-", " ").title())
            content = content.replace("my-pypulsar-app", name)
            main_py.write_text(content, encoding="utf-8")
        except Exception as e:
            typer.echo(f"Warning: Could not update main.py: {e}", err=True)

    # Upewniamy się, że folder web istnieje (na wszelki wypadek)
    web_dir = project_dir / "web"
    web_dir.mkdir(exist_ok=True)
    if not any(web_dir.iterdir()):
        (web_dir / "index.html").write_text(
            "<h1 style='text-align:center;margin-top:100px;color:#d4af37;'>Welcome to PyPulsar</h1>",
            encoding="utf-8"
        )

    typer.secho(f"Project '{name}' created successfully!", fg=typer.colors.GREEN, bold=True)
    typer.echo("\nNext steps:")
    typer.echo(f"  cd {name}")
    typer.echo("  pypulsar dev      # start in development mode")
    typer.echo("  pypulsar build    # build native app (.app/.exe)")


@app.command()
def dev():
    if not Path("main.py").exists():
        typer.secho("Error: main.py not found – run this command inside a PyPulsar project!", fg=typer.colors.RED, err=True)
        raise typer.Exit(1)
    typer.secho("Starting dev mode...", fg=typer.colors.GREEN)
    subprocess.run([sys.executable, "main.py"])


@app.command()
def build(
        onefile: bool = typer.Option(False, "--onefile", "-1", help="Build a single executable"),
        name: str = typer.Option(None, "--name", "-n", help="Application name")
):
    try:
        import PyInstaller.__main__
    except ImportError:
        typer.echo("Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "PyInstaller"])
    app_name = name or Path.cwd().name.replace(" ", "_")
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "main.py",
        "--windowed",
        "--name", app_name,
        "--add-data", f"web{os.pathsep}web"
    ]
    if sys.platform == "darwin":
        cmd.append("--argv-emulation")
    if onefile:
        cmd.append("--onefile")
    icon_path = Path("web/icon.ico") if os.name == "nt" else Path("web/icon.icns")
    if icon_path.exists():
        cmd.extend(["--icon", str(icon_path)])

    typer.secho(f"Building {app_name}...", fg=typer.colors.MAGENTA)
    subprocess.run(cmd, check=True)
    typer.secho(f"Build complete! Check dist/{app_name}/", fg=typer.colors.GREEN)


@app.command("list-templates")
def list_templates():
    templates = [p.name for p in TEMPLATES_DIR.iterdir() if p.is_dir()]
    typer.echo(f"Available templates:")
    for t in sorted(templates):
        typer.echo(f" - {t}")

@app.command()
def doctor():
    checks = []
    ok = "Success"
    warn = "Warning"
    fail = "Error"

    def add(check: str, status: str, message: str):
        checks.append((check, status, message))

    import sys
    py_ver = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    if sys.version_info >= (3, 9):
        add("Python", ok, f"{py_ver}")
    else:
        add("Python", fail, f"{py_ver} → minimum 3.9 required")

    try:
        import webview
        try:
            version = webview.__about__.__version__
        except AttributeError:
            try:
                version = webview.__version__
            except AttributeError:
                from importlib.metadata import version
                version = version("pywebview")
        add("pywebview", ok, f"v{version}")
    except Exception as e:
        add("pywebview", fail, f"import failed: {e}")

    try:
        import aiohttp
        add("aiohttp", ok, f"v{aiohttp.__version__}")
    except ImportError:
        add("aiohttp", fail, "not installed → pip install aiohttp")

    import platform
    system = platform.system()
    if system == "Darwin":
        add("Platform", ok, "macOS – using Cocoa/WebKit")
    elif system == "Windows":
        add("Platform", ok, "Windows – using Edge WebView2")
    elif system == "Linux":
        try:
            import webview.platforms.gtk
            add("Platform", ok, "Linux – using GTK/WebKit")
        except Exception:
            add("Platform", warn, "Linux – GTK not available (try gtk3 + webkitgtk-3.0)")
    else:
        add("Platform", warn, f"{system} – experimental support")

    try:
        import PyInstaller
        add("PyInstaller", ok, f"v{PyInstaller.__version__}")
    except ImportError:
        add("PyInstaller", warn, "not installed (optional) → pip install pyinstaller")

    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        port_free = s.connect_ex(('127.0.0.1', 8080)) != 0
    add("Port 8080", ok if port_free else warn, "free" if port_free else "occupied")

    has_main = (Path.cwd() / "main.py").exists()
    has_web = (Path.cwd() / "web").exists()
    if has_main and has_web:
        add("Project structure", ok, "valid PyPulsar project")
    elif has_main:
        add("Project structure", warn, "main.py found, but missing web/ folder")
    else:
        add("Project structure", warn, "not inside a PyPulsar project")

    typer.secho("\nPyPulsar Doctor – Environment Check", fg=typer.colors.CYAN, bold=True)

    all_good = True
    for name, status, msg in checks:
        icon = "Success" if status == ok else ("Warning" if status == warn else "Error")
        color = typer.colors.GREEN if status == ok else (typer.colors.YELLOW if status == warn else typer.colors.RED)
        typer.secho(f" {icon} {name:<18} → {msg}", fg=color)
        if status == fail:
            all_good = False

    typer.echo("")
    if all_good:
        typer.secho("Your system is perfectly ready for PyPulsar!", fg=typer.colors.GREEN, bold=True)
        typer.secho("Run: pypulsar dev", bold=True)
    else:
        typer.secho("Fix the errors above and run again: pypulsar doctor", fg=typer.colors.YELLOW)

@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: Optional[bool] = typer.Option(
        None, "--version", "-v", is_eager=True, help="Show version and exit"
    ),
):
    """
    PyPulsar – the modern Python desktop framework

    Build beautiful, secure, native desktop apps with Python and web technologies.
    """
    if version:
        from importlib.metadata import version, PackageNotFoundError
        try:
            v = version("pypulsar")
            typer.echo(f"PyPulsar CLI v{v}")
        except PackageNotFoundError:
            typer.echo("PyPulsar CLI (development version)")
        raise typer.Exit()

    # Jeśli nie podano żadnej komendy – pokaż help
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit()