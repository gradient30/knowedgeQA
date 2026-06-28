from pathlib import Path
import subprocess
import sys


def test_app_models_do_not_use_pydantic_v1_class_config():
    app_root = Path(__file__).resolve().parents[1] / "app"
    offenders = []

    for path in app_root.rglob("*.py"):
        if "class Config" in path.read_text(encoding="utf-8"):
            offenders.append(str(path.relative_to(app_root.parent)))

    assert offenders == []


def test_security_module_imports_without_deprecation_warnings():
    result = subprocess.run(
        [
            sys.executable,
            "-W",
            "error::DeprecationWarning",
            "-c",
            "import app.core.security",
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
