from pathlib import Path
from datetime import datetime


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def make_run_root(model_name: str, template_name: str, base_dir: Path | None = None) -> Path:
    if base_dir is None:
        base_dir = Path("runs")
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    run_dir = base_dir / f"{timestamp}_{model_name}_{template_name}"
    ensure_dir(run_dir)
    return run_dir


def module_run_dir(run_root: Path, module_stem: str) -> Path:
    mod_dir = run_root / module_stem
    ensure_dir(mod_dir)
    return mod_dir


def write_text(path: Path, content: str) -> None:
    ensure_dir(path.parent)
    path.write_text(content, encoding="utf-8")


