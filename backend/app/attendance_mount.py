import os
import importlib.util
from typing import Any


def get_flask_app() -> Any:
    """Import the Flask app from backend/flask_app.py."""
    backend_root = os.path.dirname(os.path.dirname(__file__))
    app_py = os.path.join(backend_root, "flask_app.py")
    if not os.path.exists(app_py):
        raise FileNotFoundError(f"Flask app not found at {app_py}")

    spec = importlib.util.spec_from_file_location("face_backend_app", app_py)
    if spec is None or spec.loader is None:
        raise ImportError("Unable to load face backend app module spec")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[attr-defined]

    if not hasattr(module, "app"):
        raise AttributeError("flask_app.py does not define 'app'")
    return getattr(module, "app")

