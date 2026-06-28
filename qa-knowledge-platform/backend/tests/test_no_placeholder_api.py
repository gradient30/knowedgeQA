from pathlib import Path


def test_backend_api_modules_do_not_expose_placeholder_responses():
    app_root = Path(__file__).resolve().parents[1] / "app"
    offenders = []

    for path in app_root.rglob("*.py"):
        content = path.read_text(encoding="utf-8")
        if "功能开发中" in content or "开发中" in content:
            offenders.append(str(path.relative_to(app_root.parent)))

    assert offenders == []
